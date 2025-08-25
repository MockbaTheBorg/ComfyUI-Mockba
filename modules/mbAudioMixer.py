"""
4-input audio mixer node with per-input volume sliders.

This node accepts up to four audio inputs (any iterable of samples or scalars)
and mixes them together using per-input volume sliders. If any input is an
iterable (list/tuple/etc.) the output will be a list mixed element-wise and
padded with zeros for shorter inputs. If all inputs are scalars the output
will be a scalar mix.
"""

from .common import any_typ


class mbAudioMixer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "in1": (any_typ,),
                "in2": (any_typ,),
                "in3": (any_typ,),
                "in4": (any_typ,),
                "vol1": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0}),
                "vol2": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0}),
                "vol3": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0}),
                "vol4": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0}),
            }
        }

    # Node metadata
    TITLE = "Audio Mixer"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("mixed",)
    FUNCTION = "mix"
    CATEGORY = "unset"
    DESCRIPTION = "Mix up to four audio inputs with per-input volume sliders."

    def mix(self, in1, in2, in3, in4, vol1, vol2, vol3, vol4):
        inputs = [in1, in2, in3, in4]
        vols = [vol1, vol2, vol3, vol4]

        # Normalize volumes
        for i in range(len(vols)):
            if vols[i] is None:
                vols[i] = 1.0

        # Detect audio-dict inputs (expected shape: audio_obj['waveform'])
        is_audio_obj = any(isinstance(inp, dict) and "waveform" in inp for inp in inputs if inp is not None)

        if is_audio_obj:
            # Prefer torch tensors for compatibility with ComfyUI audio helpers
            try:
                import torch
            except Exception:
                # If torch isn't available, fall back to previous behavior
                is_audio_obj = False

        if is_audio_obj:
            import torch

            # Collect waveforms and sample rates
            waveforms = []
            sample_rate = None
            max_samples = 0
            for inp in inputs:
                if inp is None:
                    waveforms.append(None)
                    continue
                if isinstance(inp, dict) and "waveform" in inp:
                    wf = inp["waveform"]
                    # Move tensors to CPU for shape inspection but keep dtype
                    if isinstance(wf, torch.Tensor):
                        t = wf.cpu().to(torch.float32)
                    else:
                        # try to convert iterable to tensor
                        try:
                            t = torch.tensor(list(wf), dtype=torch.float32)
                        except Exception:
                            # incompatible, treat as None
                            waveforms.append(None)
                            continue

                    # Normalize dims to (batch, channels, samples)
                    if t.dim() == 1:
                        t = t.unsqueeze(0).unsqueeze(0)
                    elif t.dim() == 2:
                        # assume (channels, samples) -> add batch dim
                        t = t.unsqueeze(0)
                    # else assume already (batch, channels, samples)

                    samples = t.shape[-1]
                    if samples > max_samples:
                        max_samples = samples

                    waveforms.append(t)

                    # pick sample_rate if available
                    if sample_rate is None and isinstance(inp.get("sample_rate", None), int):
                        sample_rate = inp.get("sample_rate")
                else:
                    # Non-audio-dict values: try to use as scalar signal
                    try:
                        scalar = float(inp)
                    except Exception:
                        waveforms.append(None)
                        continue
                    waveforms.append(scalar)

            # Build a mixed tensor of shape (batch=1, channels=1, samples=max_samples)
            mixed = torch.zeros((1, 1, max_samples), dtype=torch.float32)
            for idx, wf in enumerate(waveforms):
                vol = float(vols[idx]) if vols[idx] is not None else 1.0
                if wf is None:
                    continue
                if isinstance(wf, torch.Tensor):
                    # Expand channels and batch dims to (1, C, S)
                    t = wf
                    if t.dim() == 3:
                        # Use first batch if multiple
                        t = t[0]
                    if t.dim() == 2:
                        # (channels, samples)
                        c, s = t.shape
                        # collapse channels into 1 if needed by averaging
                        if c != 1:
                            t = t.mean(dim=0, keepdim=True)
                        t = t.unsqueeze(0)  # (1, 1, samples)
                    elif t.dim() == 1:
                        t = t.unsqueeze(0).unsqueeze(0)

                    s = t.shape[-1]
                    mixed[..., :s] += t * vol
                else:
                    # scalar value -> add constant across samples
                    try:
                        scalar = float(wf)
                        mixed += scalar * vol
                    except Exception:
                        continue

            # Return audio dict expected by ComfyUI helpers
            out = {"waveform": mixed, "sample_rate": sample_rate or 44100}
            return (out,)

        # Fallback: previous list/scalar mixing behavior
        # Determine if any input is an iterable (audio buffer)
        list_inputs = []
        max_len = 0
        for inp in inputs:
            if inp is None:
                list_inputs.append(None)
                continue
            # Treat strings/bytes as scalars, not iterables
            if hasattr(inp, "__iter__") and not isinstance(inp, (str, bytes)):
                try:
                    lst = list(inp)
                except Exception:
                    # fallback to scalar handling
                    list_inputs.append(inp)
                    continue
                list_inputs.append(lst)
                if len(lst) > max_len:
                    max_len = len(lst)
            else:
                list_inputs.append(inp)

        # If any iterable input exists, produce an iterable output
        if max_len > 0:
            # Try to produce a torch-based audio dict (waveform) for compatibility
            try:
                import torch
                use_torch = True
            except Exception:
                use_torch = False

            if use_torch:
                mixed = torch.zeros((1, 1, max_len), dtype=torch.float32)
                for idx_input, inp in enumerate(list_inputs):
                    vol = float(vols[idx_input]) if vols[idx_input] is not None else 1.0
                    if inp is None:
                        continue
                    if hasattr(inp, "__iter__") and not isinstance(inp, (str, bytes)):
                        for i, sample in enumerate(inp):
                            try:
                                mixed[0, 0, i] += float(sample) * vol
                            except Exception:
                                pass
                    else:
                        # scalar input: add it to every sample
                        try:
                            val = float(inp)
                            mixed[0, 0, :max_len] += val * vol
                        except Exception:
                            pass

                out = {"waveform": mixed, "sample_rate": 44100}
                return (out,)

            # Fallback to plain Python list if torch isn't available
            out = [0.0] * max_len
            for idx_input, inp in enumerate(list_inputs):
                vol = vols[idx_input]
                if inp is None:
                    continue
                if hasattr(inp, "__iter__") and not isinstance(inp, (str, bytes)):
                    for i, sample in enumerate(inp):
                        try:
                            out[i] += sample * vol
                        except Exception:
                            # ignore incompatible sample types
                            pass
                else:
                    # scalar input: add it to every sample
                    for i in range(max_len):
                        try:
                            out[i] += inp * vol
                        except Exception:
                            pass
            return (out,)

        # Scalar mixing path
        total = 0.0
        any_present = False
        for idx_input, inp in enumerate(list_inputs):
            if inp is None:
                continue
            vol = vols[idx_input]
            try:
                total += inp * vol
                any_present = True
            except Exception:
                # ignore incompatible types
                pass

        if not any_present:
            return (None,)
        return (total,)
