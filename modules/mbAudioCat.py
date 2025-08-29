"""
Audio Concatenator Node for ComfyUI
Concatenates multiple audio files with optional silence between them.
"""

import torch
from .common import any_typ


class mbAudioCat:
    """Concatenate multiple audio files with optional silence gaps."""

    def __init__(self):
        """Initialize the audio concatenator node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for audio concatenation."""
        return {
            "required": {
                "audio1": (any_typ, {
                    "tooltip": "First audio file to concatenate"
                }),
                "silence_ms": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 10000,
                    "tooltip": "Silence duration in milliseconds between audio files"
                }),
            }
        }

    # Node metadata
    TITLE = "Audio Concatenator"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("audio",)
    FUNCTION = "concatenate_audio"
    CATEGORY = "unset"  # Will be set by __init__.py
    DESCRIPTION = "Concatenate multiple audio files with optional silence gaps."

    def concatenate_audio(self, **kwargs):
        """
        Concatenate multiple audio inputs with silence gaps.

        Args:
            **kwargs: Variable number of audio inputs (audio1 is required, others optional)
                     and silence_ms parameter

        Returns:
            tuple: Concatenated audio dictionary
        """
        try:
            # Extract silence duration
            silence_ms = kwargs.get("silence_ms", 0)

            # Extract audio inputs
            audio_inputs = self._extract_audio_inputs(kwargs)

            if len(audio_inputs) == 0:
                raise ValueError("No valid audio inputs provided")

            if len(audio_inputs) == 1:
                return (audio_inputs[0],)

            # Process and concatenate audio
            concatenated_audio = self._concatenate_audio_files(audio_inputs, silence_ms)
            return (concatenated_audio,)

        except Exception as e:
            error_msg = f"Failed to concatenate audio: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)

    def _extract_audio_inputs(self, kwargs):
        """Extract audio inputs from kwargs, excluding non-audio parameters."""
        audio_inputs = []
        for key, value in kwargs.items():
            if key.startswith("audio") and key != "silence_ms":
                if isinstance(value, dict) and "waveform" in value:
                    # Extract the number from the key (e.g., "audio1" -> 1)
                    try:
                        input_num = int(key[5:])  # Remove "audio" prefix
                        audio_inputs.append((input_num, value))
                    except ValueError:
                        continue
        
        # Sort by input number and return just the audio objects
        audio_inputs.sort(key=lambda x: x[0])
        return [audio for _, audio in audio_inputs]

    def _concatenate_audio_files(self, audio_inputs, silence_ms):
        """Concatenate audio files with silence gaps."""
        if not audio_inputs:
            return None

        # Use properties from first audio input as reference
        reference_audio = audio_inputs[0]
        sample_rate = reference_audio.get("sample_rate", 44100)

        # Convert silence duration to samples
        silence_samples = int((silence_ms / 1000.0) * sample_rate)

        # Collect all waveforms
        waveforms = []
        for audio in audio_inputs:
            if isinstance(audio, dict) and "waveform" in audio:
                waveform = audio["waveform"]

                # Ensure waveform is a torch tensor
                if not isinstance(waveform, torch.Tensor):
                    try:
                        waveform = torch.tensor(waveform, dtype=torch.float32)
                    except Exception:
                        continue

                # Normalize to (batch, channels, samples) format
                if waveform.dim() == 1:
                    waveform = waveform.unsqueeze(0).unsqueeze(0)
                elif waveform.dim() == 2:
                    waveform = waveform.unsqueeze(0)

                waveforms.append(waveform)

        if not waveforms:
            raise ValueError("No valid waveforms found")

        # Concatenate waveforms with silence
        concatenated_waveform = waveforms[0]

        for i in range(1, len(waveforms)):
            if silence_samples > 0:
                # Create silence tensor with same shape as current waveform
                current_waveform = waveforms[i]
                silence_shape = list(current_waveform.shape)
                silence_shape[-1] = silence_samples
                silence_tensor = torch.zeros(silence_shape, dtype=current_waveform.dtype)

                # Concatenate previous result + silence + current waveform
                concatenated_waveform = torch.cat([
                    concatenated_waveform,
                    silence_tensor,
                    current_waveform
                ], dim=-1)
            else:
                # No silence, just concatenate
                concatenated_waveform = torch.cat([
                    concatenated_waveform,
                    waveforms[i]
                ], dim=-1)

        # Return concatenated audio in same format as input
        return {
            "waveform": concatenated_waveform,
            "sample_rate": sample_rate
        }
