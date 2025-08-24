"""
Simple Data Type Converter Node for ComfyUI
This simplified node converts any tensor-like input to the requested torch dtype.
It intentionally treats any tensor-like value as a tensor and converts it without
special-casing images, audio, masks, or containers.
"""

# Local imports
from .common import any_typ

# Standard/third-party
import torch
import numpy as np


class mbDataTypeConverter:
    """Minimal converter: coerce input to torch.Tensor and convert dtype."""

    SUPPORTED_DTYPES = [
        "float32", "float16", "bfloat16",
        "int32", "int16", "int8",
        "uint8", "bool",
        "float64", "int64"
    ]

    DTYPE_MAPPING = {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "int32": torch.int32,
        "int16": torch.int16,
        "int8": torch.int8,
        "uint8": torch.uint8,
        "bool": torch.bool,
        "float64": torch.float64,
        "int64": torch.int64
    }

    DEFAULT_DTYPE = "float16"

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tensor": (any_typ, {
                    "tooltip": "Tensor-like input to convert (torch.Tensor, numpy array, list, etc.)"
                }),
                "target_dtype": (cls.SUPPORTED_DTYPES, {
                    "default": cls.DEFAULT_DTYPE,
                    "tooltip": "Target dtype to convert the tensor to"
                })
            }
        }

    TITLE = "Data Type Converter"
    RETURN_TYPES = (any_typ, "STRING")
    RETURN_NAMES = ("converted_tensor", "status")
    FUNCTION = "convert"
    CATEGORY = "unset"
    DESCRIPTION = "Convert any tensor-like input to the chosen torch dtype (minimal, no heuristics)."

    def convert(self, tensor, target_dtype):
        """
        Convert input to target dtype.
        If input is not convertible to a torch tensor, returns original input and an error message.
        """
        try:
            # Resolve target dtype
            if target_dtype not in self.DTYPE_MAPPING:
                return (tensor, f"Unsupported target dtype: {target_dtype}")

            target_torch_dtype = self.DTYPE_MAPPING[target_dtype]

            # If input is a container, recursively convert contained tensors
            if isinstance(tensor, (dict, list, tuple)):
                converted, count = self._convert_any_item(tensor, target_torch_dtype)
                status = f"Converted {count} tensor(s) to {target_torch_dtype}"
                return (converted, status)

            # Single item: try to coerce to tensor and convert
            if isinstance(tensor, torch.Tensor):
                t = tensor
            else:
                try:
                    if isinstance(tensor, np.ndarray):
                        t = torch.from_numpy(tensor)
                    else:
                        t = torch.as_tensor(tensor)
                except Exception as e:
                    return (tensor, f"Not convertible to torch.Tensor: {e}")

            # Preserve device if possible
            orig_device = t.device if hasattr(t, 'device') else None

            # Perform conversion with value-range mapping
            converted = self._map_tensor_dtype(t, target_torch_dtype)

            # Move back to original device if needed
            if orig_device is not None and converted.device != orig_device:
                try:
                    converted = converted.to(orig_device)
                except Exception:
                    pass

            return (converted, f"Converted to {target_torch_dtype}")

        except Exception as e:
            return (tensor, f"Error during conversion: {e}")

    def _convert_any_item(self, item, target_torch_dtype):
        """Recursively convert tensors/numpy arrays inside containers.

        Returns (converted_item, count_of_converted_tensors)
        """
        count = 0

        # Torch tensor
        if isinstance(item, torch.Tensor):
            try:
                converted = self._map_tensor_dtype(item, target_torch_dtype)
                return converted, 1
            except Exception:
                return item, 0

        # Numpy array -> torch
        if isinstance(item, np.ndarray):
            try:
                t = torch.from_numpy(item)
                conv, c = self._convert_any_item(t, target_torch_dtype)
                return conv, c
            except Exception:
                return item, 0

        # dict
        if isinstance(item, dict):
            out = {}
            for k, v in item.items():
                conv_v, c = self._convert_any_item(v, target_torch_dtype)
                out[k] = conv_v
                count += c
            return out, count

        # list
        if isinstance(item, list):
            out_list = []
            for v in item:
                conv_v, c = self._convert_any_item(v, target_torch_dtype)
                out_list.append(conv_v)
                count += c
            return out_list, count

        # tuple
        if isinstance(item, tuple):
            out_list = []
            for v in item:
                conv_v, c = self._convert_any_item(v, target_torch_dtype)
                out_list.append(conv_v)
                count += c
            return tuple(out_list), count

        # not convertible
        return item, 0

    def _get_dtype_limits(self, torch_dtype, sample_tensor=None):
        """Return (min, max) representable values for a torch dtype.

        For floating types, if a sample_tensor is provided and its absolute max <= 1.5,
        the function assumes a normalized range (-1,1) for mapping purposes; otherwise
        it uses the dtype's full finfo range.
        """
        if torch_dtype == torch.bool:
            return 0.0, 1.0

        if torch.is_floating_point(torch.empty(1, dtype=torch_dtype)):
            # Heuristic: treat small-magnitude floats as normalized audio [-1,1]
            if sample_tensor is not None:
                try:
                    max_abs = float(sample_tensor.abs().max())
                except Exception:
                    max_abs = None
                if max_abs is not None and max_abs <= 1.5:
                    return -1.0, 1.0

            info = torch.finfo(torch_dtype)
            return float(info.min), float(info.max)

        # Integer types
        info = torch.iinfo(torch_dtype)
        return float(info.min), float(info.max)

    def _map_tensor_dtype(self, tensor, target_torch_dtype):
        """Map tensor values from source dtype range to target dtype range and cast.

        Uses float64 intermediate math to avoid precision loss, clamps to target range,
        and rounds when converting to integer target dtypes.
        """
        # If dtypes are equal, just return a copy / same tensor
        src_dtype = tensor.dtype
        tgt_dtype = target_torch_dtype
        if src_dtype == tgt_dtype:
            return tensor

        # Get device to preserve
        device = tensor.device if hasattr(tensor, 'device') else None

        # If both source and target are floating point, preserve numeric values (no full-range mapping)
        if torch.is_floating_point(torch.empty(1, dtype=src_dtype)) and torch.is_floating_point(torch.empty(1, dtype=tgt_dtype)):
            out = tensor.to(tgt_dtype)
            if device is not None and out.device != device:
                try:
                    out = out.to(device)
                except Exception:
                    pass
            return out

        # Determine numeric ranges
        src_min, src_max = self._get_dtype_limits(src_dtype, sample_tensor=tensor if torch.is_floating_point(tensor) else None)
        tgt_min, tgt_max = self._get_dtype_limits(tgt_dtype)

        # Avoid zero division
        if src_max == src_min:
            frac = torch.full_like(tensor, 0.5, dtype=torch.float64)
        else:
            # Perform mapping in float64
            x = tensor.to(torch.float64)
            frac = (x - src_min) / (src_max - src_min)

        frac = frac.clamp(0.0, 1.0)

        mapped = frac * (tgt_max - tgt_min) + tgt_min

        # Cast to target dtype
        if torch.is_floating_point(torch.empty(1, dtype=tgt_dtype)):
            out = mapped.to(tgt_dtype)
        else:
            # integer or bool: round then cast
            out = mapped.round().to(tgt_dtype)

        # Ensure device preservation
        if device is not None and out.device != device:
            try:
                out = out.to(device)
            except Exception:
                pass

        return out
