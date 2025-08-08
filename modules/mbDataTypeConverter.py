"""
Data Type Converter Node for ComfyUI
Converts tensor data types for memory optimization and performance tuning with detailed analysis.
"""

# Standard library imports
import torch
import numpy as np

# Local imports
from .common import any_typ, CATEGORIES


class mbDataTypeConverter:
    """Convert tensor data types with comprehensive memory analysis and optimization reporting."""
    
    # Class constants
    SUPPORTED_DTYPES = [
        "float32", "float16", "bfloat16",
        "int32", "int16", "int8", 
        "uint8", "bool",
        "float64", "int64"
    ]
    DEFAULT_DTYPE = "float16"
    DEFAULT_SHOW_MEMORY = True
    
    # Data type mapping and information
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
    
    # Memory unit thresholds
    BYTES_PER_KB = 1024
    BYTES_PER_MB = 1024 ** 2
    BYTES_PER_GB = 1024 ** 3
    
    def __init__(self):
        """Initialize the data type converter node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for data type conversion."""
        return {
            "required": {
                "tensor": (any_typ, {
                    "tooltip": "Input tensor to convert (any tensor type)"
                }),
                "target_dtype": (cls.SUPPORTED_DTYPES, {
                    "default": cls.DEFAULT_DTYPE,
                    "tooltip": "Target data type for conversion"
                }),
                "show_memory_info": ("BOOLEAN", {
                    "default": cls.DEFAULT_SHOW_MEMORY,
                    "tooltip": "Display detailed memory usage analysis"
                }),
            }
        }

    # Node metadata
    RETURN_TYPES = (any_typ, "STRING")
    RETURN_NAMES = ("converted_tensor", "memory_info")
    FUNCTION = "convert_data_type"
    CATEGORY = CATEGORIES["DATA_MANAGEMENT"]
    DESCRIPTION = "Convert tensor data types for memory optimization and performance tuning with detailed memory analysis."
    OUTPUT_NODE = True

    def convert_data_type(self, tensor, target_dtype, show_memory_info):
        """
        Convert tensor to target data type with memory analysis.
        
        Args:
            tensor: Input tensor to convert
            target_dtype: Target data type string
            show_memory_info: Whether to show detailed memory information
            
        Returns:
            tuple: (converted_tensor, memory_info_string)
        """
        try:
            # Validate tensor input
            if not self._is_convertible_tensor(tensor):
                return (tensor, "Input is not a tensor - no conversion needed")
            
            # Get tensor information
            tensor_info = self._analyze_tensor(tensor)
            
            # Perform conversion
            converted_tensor, conversion_status = self._perform_conversion(tensor, target_dtype, tensor_info)
            
            # Generate memory analysis
            memory_info = self._generate_memory_analysis(
                tensor, converted_tensor, tensor_info, target_dtype, 
                conversion_status, show_memory_info
            )
            
            return (converted_tensor, memory_info)
            
        except Exception as e:
            error_msg = f"Error converting data type: {str(e)}"
            print(error_msg)
            return (tensor, error_msg)

    def _is_convertible_tensor(self, obj):
        """Check if object is a convertible tensor."""
        return hasattr(obj, 'dtype')

    def _analyze_tensor(self, tensor):
        """Analyze tensor properties for conversion."""
        return {
            'original_dtype': tensor.dtype,
            'device': tensor.device if hasattr(tensor, 'device') else 'unknown',
            'shape': tuple(tensor.shape),
            'original_size': tensor.numel() * tensor.element_size() if hasattr(tensor, 'numel') else 0
        }

    def _perform_conversion(self, tensor, target_dtype, tensor_info):
        """Perform the actual data type conversion."""
        # Validate target data type
        if target_dtype not in self.DTYPE_MAPPING:
            raise ValueError(f"Unsupported data type: {target_dtype}")
        
        target_torch_dtype = self.DTYPE_MAPPING[target_dtype]
        
        # Check if conversion is needed
        if tensor_info['original_dtype'] == target_torch_dtype:
            return tensor, "No conversion needed - already target type"
        
        # Perform conversion
        converted_tensor = tensor.to(target_torch_dtype)
        return converted_tensor, "Conversion successful"

    def _generate_memory_analysis(self, original_tensor, converted_tensor, tensor_info, 
                                target_dtype, conversion_status, show_detailed_info):
        """Generate comprehensive memory usage analysis."""
        new_size = converted_tensor.numel() * converted_tensor.element_size()
        original_size = tensor_info['original_size']
        
        if show_detailed_info:
            return self._create_detailed_memory_report(
                tensor_info, target_dtype, original_size, new_size, conversion_status
            )
        else:
            return f"{tensor_info['original_dtype']} → {self.DTYPE_MAPPING[target_dtype]}"

    def _create_detailed_memory_report(self, tensor_info, target_dtype, original_size, new_size, status):
        """Create detailed memory usage report."""
        memory_ratio = new_size / original_size if original_size > 0 else 1.0
        memory_saved = original_size - new_size
        
        info_lines = [
            "Data Type Conversion:",
            f"  {tensor_info['original_dtype']} → {self.DTYPE_MAPPING[target_dtype]}",
            f"  Device: {tensor_info['device']}",
            f"  Shape: {tensor_info['shape']}",
            "",
            "Memory Usage:",
            f"  Original: {self._format_bytes(original_size)}",
            f"  New: {self._format_bytes(new_size)}",
            f"  Ratio: {memory_ratio:.2f}x",
        ]
        
        # Add memory change information
        if memory_saved > 0:
            info_lines.append(f"  Saved: {self._format_bytes(memory_saved)} ({(1-memory_ratio)*100:.1f}%)")
        elif memory_saved < 0:
            info_lines.append(f"  Increased: {self._format_bytes(-memory_saved)} ({(memory_ratio-1)*100:.1f}%)")
        else:
            info_lines.append("  No change")
        
        info_lines.extend([
            "",
            f"Status: {status}"
        ])
        
        return "\n".join(info_lines)

    def _format_bytes(self, bytes_val):
        """Format byte values in human-readable format."""
        if bytes_val < self.BYTES_PER_KB:
            return f"{bytes_val} B"
        elif bytes_val < self.BYTES_PER_MB:
            return f"{bytes_val/self.BYTES_PER_KB:.1f} KB"
        elif bytes_val < self.BYTES_PER_GB:
            return f"{bytes_val/self.BYTES_PER_MB:.1f} MB"
        else:
            return f"{bytes_val/self.BYTES_PER_GB:.1f} GB"

    @classmethod
    def get_dtype_info(cls):
        """
        Get comprehensive information about supported data types.
        
        Returns:
            dict: Data type information including memory usage, range, and precision
        """
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
