import torch
import numpy as np
from .common import any_typ

class mbDataTypeConverter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tensor": (any_typ, {}),
                "target_dtype": ([
                    "float32", "float16", "bfloat16",
                    "int32", "int16", "int8", 
                    "uint8", "bool",
                    "float64", "int64"
                ], {"default": "float16"}),
                "show_memory_info": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = (any_typ, "STRING")
    RETURN_NAMES = ("converted_tensor", "memory_info")
    FUNCTION = "convert_dtype"
    CATEGORY = "🖖 Mockba/utility"
    DESCRIPTION = "Convert tensor data types for memory optimization and performance"
    OUTPUT_NODE = True

    def convert_dtype(self, tensor, target_dtype, show_memory_info):
        try:
            # Check if input has dtype attribute (is a tensor)
            if not hasattr(tensor, 'dtype'):
                return (tensor, "Input is not a tensor - no conversion needed")
            
            original_dtype = tensor.dtype
            original_device = tensor.device if hasattr(tensor, 'device') else 'unknown'
            
            # Calculate original memory usage
            original_size = tensor.numel() * tensor.element_size() if hasattr(tensor, 'numel') else 0
            
            # Map string dtype to torch dtype
            dtype_mapping = {
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
            
            if target_dtype not in dtype_mapping:
                return (tensor, f"Unsupported data type: {target_dtype}")
            
            target_torch_dtype = dtype_mapping[target_dtype]
            
            # Convert the tensor
            if original_dtype == target_torch_dtype:
                converted_tensor = tensor
                conversion_status = "No conversion needed - already target type"
            else:
                converted_tensor = tensor.to(target_torch_dtype)
                conversion_status = "Conversion successful"
            
            # Calculate new memory usage
            new_size = converted_tensor.numel() * converted_tensor.element_size()
            memory_ratio = new_size / original_size if original_size > 0 else 1.0
            memory_saved = original_size - new_size
            
            # Format memory info
            def format_bytes(bytes_val):
                if bytes_val < 1024:
                    return f"{bytes_val} B"
                elif bytes_val < 1024**2:
                    return f"{bytes_val/1024:.1f} KB"
                elif bytes_val < 1024**3:
                    return f"{bytes_val/(1024**2):.1f} MB"
                else:
                    return f"{bytes_val/(1024**3):.1f} GB"
            
            if show_memory_info:
                info_lines = [
                    f"Data Type Conversion:",
                    f"  {original_dtype} → {target_torch_dtype}",
                    f"  Device: {original_device}",
                    f"  Shape: {tuple(tensor.shape)}",
                    f"",
                    f"Memory Usage:",
                    f"  Original: {format_bytes(original_size)}",
                    f"  New: {format_bytes(new_size)}",
                    f"  Ratio: {memory_ratio:.2f}x",
                ]
                
                if memory_saved > 0:
                    info_lines.append(f"  Saved: {format_bytes(memory_saved)} ({(1-memory_ratio)*100:.1f}%)")
                elif memory_saved < 0:
                    info_lines.append(f"  Increased: {format_bytes(-memory_saved)} ({(memory_ratio-1)*100:.1f}%)")
                else:
                    info_lines.append(f"  No change")
                
                info_lines.extend([
                    f"",
                    f"Status: {conversion_status}"
                ])
                
                memory_info = "\n".join(info_lines)
            else:
                memory_info = f"{original_dtype} → {target_torch_dtype}"
            
            return (converted_tensor, memory_info)
            
        except Exception as e:
            error_msg = f"Error converting data type: {str(e)}"
            print(error_msg)
            return (tensor, error_msg)

    @classmethod
    def get_dtype_info(cls):
        """Helper method to get information about different data types"""
        return {
            "float32": {"bytes": 4, "range": "±1.2e-38 to ±3.4e+38", "precision": "~7 decimal digits"},
            "float16": {"bytes": 2, "range": "±6.1e-5 to ±6.5e+4", "precision": "~3 decimal digits"},
            "bfloat16": {"bytes": 2, "range": "±1.2e-38 to ±3.4e+38", "precision": "~2 decimal digits"},
            "int32": {"bytes": 4, "range": "-2,147,483,648 to 2,147,483,647", "precision": "exact"},
            "int16": {"bytes": 2, "range": "-32,768 to 32,767", "precision": "exact"},
            "int8": {"bytes": 1, "range": "-128 to 127", "precision": "exact"},
            "uint8": {"bytes": 1, "range": "0 to 255", "precision": "exact"},
            "bool": {"bytes": 1, "range": "True/False", "precision": "exact"},
            "float64": {"bytes": 8, "range": "±2.2e-308 to ±1.8e+308", "precision": "~15 decimal digits"},
            "int64": {"bytes": 8, "range": "±9.2e+18", "precision": "exact"}
        }
