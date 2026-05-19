"""
Debug Information Node for ComfyUI
Displays comprehensive debug information about any input object.
"""

from pprint import pformat

from .common import any_typ


class mbDebug:
    """Display comprehensive debug information about any input object."""

    SEPARATOR_LINE = "-" * 60
    SAMPLE_LIMIT = 10
    STATS_ELEMENT_LIMIT = 1_000_000

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input": (any_typ, {"tooltip": "Any object to debug and analyze"}),
            }
        }

    TITLE = "Debug Information"
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "debug_object"
    CATEGORY = "unset"
    DESCRIPTION = "Display comprehensive debug information about any input object in a text widget."
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        import time

        return time.time()

    def debug_object(self, input):
        try:
            debug_lines = self._generate_debug_info(input)
            debug_text = "\n".join(debug_lines)
        except Exception as e:
            debug_text = f"Error: {str(e)}"

        return {"ui": {"value": [debug_text]}, "result": (debug_text,)}

    def _generate_debug_info(self, obj):
        debug_lines = []
        debug_lines.append("Debug Info:")
        debug_lines.append(self.SEPARATOR_LINE)
        debug_lines.append(f"Top-level type: {type(obj).__name__}")
        debug_lines.append("")

        if obj is None:
            debug_lines.append("Value: None")
            return debug_lines

        if self._is_torch_tensor(obj):
            debug_lines.extend(self._debug_torch_tensor(obj))
            return debug_lines

        if self._is_numpy_array(obj):
            debug_lines.extend(self._debug_numpy_array(obj))
            return debug_lines

        if self._is_pil_image(obj):
            debug_lines.extend(self._debug_pil_image(obj))
            return debug_lines

        if isinstance(obj, (list, tuple)):
            debug_lines.extend(self._debug_sequence(obj))
            return debug_lines

        if isinstance(obj, dict):
            debug_lines.extend(self._debug_mapping(obj))
            return debug_lines

        if isinstance(obj, (str, int, float, bool)):
            debug_lines.extend(self._debug_simple_value(obj))
        else:
            debug_lines.extend(self._debug_object(obj))

        return debug_lines

    def _is_torch_tensor(self, obj):
        try:
            import torch

            return isinstance(obj, torch.Tensor)
        except Exception:
            return False

    def _is_numpy_array(self, obj):
        try:
            import numpy as np

            return isinstance(obj, np.ndarray)
        except Exception:
            return hasattr(obj, "shape") and hasattr(obj, "dtype") and not self._is_torch_tensor(obj)

    def _is_pil_image(self, obj):
        try:
            from PIL import Image

            return isinstance(obj, Image.Image)
        except Exception:
            return False

    def _truncate(self, s, max_len=1000):
        try:
            s = str(s)
            if len(s) > max_len:
                return s[:max_len] + f"... (truncated, {len(s)} chars)"
            return s
        except Exception:
            return "<unrepresentable>"

    def _debug_torch_tensor(self, tensor):
        debug_lines = ["TENSOR (torch.Tensor):"]
        try:
            import numpy as _np
            dtype = str(getattr(tensor, "dtype", "N/A"))
            shape = tuple(getattr(tensor, "shape", "N/A"))
            device = getattr(tensor, "device", "N/A")
            requires_grad = getattr(tensor, "requires_grad", "N/A")
            numel = int(tensor.numel()) if hasattr(tensor, "numel") else None
            elem_size = int(tensor.element_size()) if hasattr(tensor, "element_size") else None
            mem_bytes = elem_size * numel if (elem_size is not None and numel is not None) else "N/A"

            debug_lines.append(f"  Type: {type(tensor).__name__}")
            debug_lines.append(f"  Shape: {shape}")
            debug_lines.append(f"  Dtype: {dtype}")
            debug_lines.append(f"  Device: {device}")
            debug_lines.append(f"  Requires grad: {requires_grad}")
            debug_lines.append(f"  Approx memory: {mem_bytes}")
            if numel is not None:
                debug_lines.append(f"  Num elements: {numel}")

            try:
                if numel is None or numel <= self.STATS_ELEMENT_LIMIT:
                    t_cpu = tensor.detach().cpu()
                    arr = t_cpu.numpy()
                    debug_lines.append(f"  Min: {float(_np.min(arr))}")
                    debug_lines.append(f"  Max: {float(_np.max(arr))}")
                    debug_lines.append(f"  Mean: {float(_np.mean(arr)):.6f}")
                    debug_lines.append(f"  Std: {float(_np.std(arr)):.6f}")
                    flat = arr.ravel()
                    sample = flat[: self.SAMPLE_LIMIT].tolist()
                    debug_lines.append(f"  Sample (first {min(len(flat), self.SAMPLE_LIMIT)}): {self._truncate(sample, 200)}")
                else:
                    debug_lines.append("  Statistical info: skipped (tensor too large)")
            except Exception:
                debug_lines.append("  Statistical info: unable to compute")
        except Exception as e:
            debug_lines.append(f"  Error inspecting tensor: {e}")

        debug_lines.append("")
        return debug_lines

    def _debug_numpy_array(self, arr):
        debug_lines = ["ARRAY (numpy.ndarray):"]
        try:
            import numpy as _np
            dtype = getattr(arr, "dtype", "N/A")
            shape = getattr(arr, "shape", "N/A")
            nbytes = getattr(arr, "nbytes", "N/A")
            size = int(getattr(arr, "size", "N/A")) if getattr(arr, "size", None) is not None else "N/A"

            debug_lines.append(f"  Type: {type(arr).__name__}")
            debug_lines.append(f"  Shape: {shape}")
            debug_lines.append(f"  Dtype: {dtype}")
            debug_lines.append(f"  Num elements: {size}")
            debug_lines.append(f"  Approx memory: {nbytes} bytes")

            try:
                if size == "N/A" or size <= self.STATS_ELEMENT_LIMIT:
                    debug_lines.append(f"  Min: {float(_np.nanmin(arr))}")
                    debug_lines.append(f"  Max: {float(_np.nanmax(arr))}")
                    debug_lines.append(f"  Mean: {float(_np.nanmean(arr)):.6f}")
                    debug_lines.append(f"  Std: {float(_np.nanstd(arr)):.6f}")
                    flat = arr.ravel()
                    sample = flat[: self.SAMPLE_LIMIT].tolist()
                    debug_lines.append(f"  Sample (first {min(len(flat), self.SAMPLE_LIMIT)}): {self._truncate(sample, 200)}")
                else:
                    debug_lines.append("  Statistical info: skipped (array too large)")
            except Exception:
                debug_lines.append("  Statistical info: unable to compute")
        except Exception as e:
            debug_lines.append(f"  Error inspecting array: {e}")

        debug_lines.append("")
        return debug_lines

    def _debug_pil_image(self, img):
        debug_lines = ["IMAGE (PIL.Image):"]
        try:
            from PIL import Image
            debug_lines.append(f"  Type: {type(img).__name__}")
            debug_lines.append(f"  Size (W,H): {getattr(img, 'size', 'N/A')}")
            debug_lines.append(f"  Mode: {getattr(img, 'mode', 'N/A')}")
            debug_lines.append(f"  Format: {getattr(img, 'format', 'N/A')}")
            try:
                import numpy as _np
                arr = _np.array(img)
                debug_lines.append(f"  Underlying array shape: {getattr(arr, 'shape', 'N/A')}")
                if arr.size <= self.STATS_ELEMENT_LIMIT:
                    debug_lines.append(f"  Array dtype: {arr.dtype}")
                    debug_lines.append(f"  Min: {float(arr.min())}")
                    debug_lines.append(f"  Max: {float(arr.max())}")
                    debug_lines.append(f"  Mean: {float(arr.mean()):.6f}")
                else:
                    debug_lines.append("  Array statistical info: skipped (too large)")
            except Exception:
                debug_lines.append("  Underlying array: unable to inspect")
        except Exception as e:
            debug_lines.append(f"  Error inspecting image: {e}")

        debug_lines.append("")
        return debug_lines

    def _debug_sequence(self, seq):
        debug_lines = ["SEQUENCE (list/tuple):"]
        try:
            length = len(seq)
            debug_lines.append(f"  Length: {length}")

            if length == 0:
                debug_lines.append("  (empty)")
                debug_lines.append("")
                return debug_lines

            # Scan a reasonable prefix for element types (avoid huge scans)
            max_scan = min(length, max(100, self.SAMPLE_LIMIT * 10))
            counts = {}
            indices_by_cat = {}
            for i, v in enumerate(seq[:max_scan]):
                cat = self._element_category(v)
                counts[cat] = counts.get(cat, 0) + 1
                indices_by_cat.setdefault(cat, []).append(i)

            # Show a short sample of the first items
            for i, v in enumerate(seq[: self.SAMPLE_LIMIT]):
                tname = type(v).__name__
                summary = self._short_value_summary(v)
                debug_lines.append(f"  [{i}] {tname}: {summary}")
                try:
                    # mark that detailed info exists
                    if self._is_torch_tensor(v) or self._is_numpy_array(v) or self._is_pil_image(v):
                        debug_lines.append(f"    -> contains {self._element_category(v)}; more details shown below")
                except Exception:
                    pass

            if length > self.SAMPLE_LIMIT:
                debug_lines.append(f"  ... showing first {self.SAMPLE_LIMIT} items")

            # Summarize detected element categories
            if counts:
                debug_lines.append(f"  Element types summary: {pformat(counts)}")

                # For important categories, show detailed info for up to 3 examples
                for cat in ("torch", "numpy", "pil"):
                    c = counts.get(cat, 0)
                    if c:
                        sample_idxs = indices_by_cat.get(cat, [])[:3]
                        debug_lines.append(f"  Detected {cat} elements: {c} (sample indices: {pformat(sample_idxs)})")
                        for idx in sample_idxs:
                            if idx < len(seq):
                                v = seq[idx]
                                debug_lines.append(f"    Detailed for element [{idx}]:")
                                try:
                                    if cat == "torch":
                                        nested = self._debug_torch_tensor(v)
                                    elif cat == "numpy":
                                        nested = self._debug_numpy_array(v)
                                    else:
                                        nested = self._debug_pil_image(v)
                                    debug_lines.extend(self._indent_lines(nested, prefix="    "))
                                except Exception as e:
                                    debug_lines.append(f"      Error generating detail: {e}")
            # Also generate a compact tree view of nested containers (safe, depth-limited)
            try:
                tree_lines = self._build_tree_lines(seq, name="root", max_depth=4)
                debug_lines.append("  Nested object tree:")
                debug_lines.extend(self._indent_lines(tree_lines, prefix="    "))
            except Exception as e:
                debug_lines.append(f"  Tree generation failed: {e}")
        except Exception as e:
            debug_lines.append(f"  Error inspecting sequence: {e}")

        debug_lines.append("")
        return debug_lines

    def _element_category(self, v):
        try:
            if self._is_torch_tensor(v):
                return "torch"
            if self._is_numpy_array(v):
                return "numpy"
            if self._is_pil_image(v):
                return "pil"
            if isinstance(v, dict):
                return "dict"
            if isinstance(v, list):
                return "list"
            if isinstance(v, tuple):
                return "tuple"
            if isinstance(v, str):
                return "str"
            if isinstance(v, bool):
                return "bool"
            if isinstance(v, int):
                return "int"
            if isinstance(v, float):
                return "float"
            return type(v).__name__
        except Exception:
            return "other"

    def _indent_lines(self, lines, prefix="    "):
        try:
            return [prefix + l for l in lines]
        except Exception:
            return [prefix + str(lines)]

    def _build_tree_lines(self, obj, name="root", max_depth=4):
        """Build a small ASCII tree representing nested lists/tuples/dicts.

        - Limits depth to `max_depth` and samples up to `SAMPLE_LIMIT` children.
        - Tracks visited object ids to avoid infinite recursion.
        """
        root_suffix = self._tree_suffix(obj)
        lines = [f"{name} ({type(obj).__name__}{', ' + root_suffix if root_suffix else ''})"]
        visited = set()

        def rec(o, prefix, depth):
            if depth >= max_depth:
                lines.append(prefix + "... (max depth reached)")
                return

            oid = id(o)
            if oid in visited:
                lines.append(prefix + "<recursion detected>")
                return
            visited.add(oid)

            children = []
            try:
                if isinstance(o, dict):
                    for k in list(o.keys())[: self.SAMPLE_LIMIT]:
                        children.append((f"{pformat(k)}", o[k]))
                elif isinstance(o, (list, tuple)):
                    for i, v in enumerate(o[: self.SAMPLE_LIMIT]):
                        children.append((f"[{i}]", v))
            except Exception:
                return

            for idx, (cname, child) in enumerate(children):
                is_last = idx == (len(children) - 1)
                connector = "└─" if is_last else "├─"
                suffix = self._tree_suffix(child)
                lines.append(prefix + connector + " " + cname + f" ({type(child).__name__}{', ' + suffix if suffix else ''})")
                new_prefix = prefix + ("   " if is_last else "│  ")
                rec(child, new_prefix, depth + 1)

        rec(obj, "", 0)
        return lines

    def _tree_suffix(self, obj):
        """Return a short suffix string describing dimensions/size for tree display."""
        try:
            if self._is_torch_tensor(obj):
                try:
                    return f"shape={tuple(getattr(obj, 'shape', ())) }"
                except Exception:
                    return "shape=N/A"
            if self._is_numpy_array(obj):
                return f"shape={getattr(obj, 'shape', 'N/A')}"
            if self._is_pil_image(obj):
                return f"size={getattr(obj, 'size', 'N/A')}"
            if isinstance(obj, (list, tuple)):
                return f"len={len(obj)}"
            if isinstance(obj, dict):
                return f"len={len(obj)}"
            if isinstance(obj, str):
                return f"len={len(obj)}"
            return ""
        except Exception:
            return ""

    def _debug_mapping(self, d):
        debug_lines = ["MAPPING (dict):"]
        try:
            keys = list(d.keys())
            debug_lines.append(f"  Keys: {len(keys)}")
            sample_keys = keys[: self.SAMPLE_LIMIT]
            debug_lines.append(f"  Sample keys: {pformat(sample_keys)}")
            for k in sample_keys:
                v = d[k]
                summary = self._short_value_summary(v)
                debug_lines.append(f"  Key {pformat(k)} -> {type(v).__name__}: {summary}")
            if len(keys) > self.SAMPLE_LIMIT:
                debug_lines.append(f"  ... showing first {self.SAMPLE_LIMIT} keys")
        except Exception as e:
            debug_lines.append(f"  Error inspecting mapping: {e}")

        debug_lines.append("")
        return debug_lines

    def _short_value_summary(self, v):
        try:
            if self._is_torch_tensor(v):
                return f"torch {tuple(v.shape)} {getattr(v, 'dtype', 'N/A')}"
            if self._is_numpy_array(v):
                return f"np {getattr(v, 'shape', 'N/A')} {getattr(v, 'dtype', 'N/A')}"
            if self._is_pil_image(v):
                return f"PIL size={getattr(v, 'size', 'N/A')} mode={getattr(v, 'mode', 'N/A')}"
            if isinstance(v, (list, tuple)):
                return f"seq(len={len(v)})"
            if isinstance(v, dict):
                return f"dict(len={len(v)})"
            if isinstance(v, (str, int, float, bool)):
                return self._truncate(v, 200)
            return self._truncate(repr(v), 200)
        except Exception:
            return "<unrepresentable>"

    def _debug_object(self, obj):
        debug_lines = ["OBJECT INFORMATION:"]
        try:
            debug_lines.append(f"  Type: {type(obj).__name__}")
            try:
                attrs = [a for a in dir(obj) if not a.startswith("_")]
                methods = [a for a in attrs if callable(getattr(obj, a, None))]
                props = [a for a in attrs if not callable(getattr(obj, a, None))]
                debug_lines.append(f"  Public attributes: {len(attrs)} (methods: {len(methods)}, props: {len(props)})")
                if props:
                    debug_lines.append(f"  Props sample: {pformat(props[:20])}")
                if methods:
                    debug_lines.append(f"  Methods sample: {pformat(methods[:20])}")
            except Exception:
                debug_lines.append("  Unable to list attributes")
            try:
                debug_lines.append(f"  repr: {self._truncate(repr(obj), 500)}")
            except Exception:
                pass
        except Exception as e:
            debug_lines.append(f"  Error inspecting object: {e}")

        debug_lines.append("")
        return debug_lines

    def _debug_simple_value(self, obj):
        debug_lines = ["VALUE INFORMATION:"]
        debug_lines.append(f"  Type: {type(obj).__name__}")
        try:
            debug_lines.append(f"  Value: {self._truncate(obj, 500)}")
        except Exception:
            debug_lines.append("  Value: <unrepresentable>")

        debug_lines.append("")
        return debug_lines
