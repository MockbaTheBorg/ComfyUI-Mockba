"""
Universal Display Node for ComfyUI
Shows information about any input type with automatic formatting and multiline detection.
"""

# Standard library imports
import torch
import numpy as np
from pprint import pformat

# Local imports
from .common import any_typ, CATEGORIES


class mbDisplay:
    """Universal display node that shows information about any input type."""
    
    # Class constants
    DEFAULT_MESSAGE = "Display output will appear here after execution..."
    MAX_DICT_KEYS = 10
    MAX_STRING_LENGTH = 200
    PFORMAT_WIDTH = 60
    PFORMAT_DEPTH = 2
    
    def __init__(self):
        """Initialize the display node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for universal display."""
        return {
            "required": {
                "input": (any_typ, {
                    "tooltip": "Any type of data to display"
                }),
                "value": ("STRING", {
                    "multiline": False, 
                    "default": cls.DEFAULT_MESSAGE,
                    "tooltip": "Display output (automatically populated)"
                }),
            }
        }

    # Node metadata
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "display_data"
    CATEGORY = CATEGORIES["DEVELOPMENT"]
    DESCRIPTION = "Universal display node that shows information about any input type - strings, numbers, images, tensors, etc."
    OUTPUT_NODE = True

    def display_data(self, input, value):
        """
        Display information about the input data.
        
        Args:
            input: Any type of data to analyze and display
            value: Current display value (updated by this function)
            
        Returns:
            dict: UI update with formatted display text and multiline setting
        """
        try:
            display_text = self._format_data(input)
        except Exception as e:
            display_text = f"Error: {str(e)}"
        
        # Determine if multiline display is needed
        has_newlines = '\n' in display_text
        
        return {
            "ui": {"value": [display_text]},
            "result": (display_text,),
            "multiline": has_newlines
        }

    def _format_data(self, input):
        """Format input data for display based on its type."""
        # Handle None
        if input is None:
            return "None"
        
        # Handle basic types
        if isinstance(input, (str, int, float, bool)):
            return str(input)
        
        # Handle collections
        if isinstance(input, (list, tuple)):
            return str(input)
        
        # Handle dictionaries
        if isinstance(input, dict):
            return self._format_dict(input)
        
        # Handle tensors
        if hasattr(input, 'shape') and hasattr(input, 'dtype'):
            return self._format_tensor(input)
        
        # Handle numpy arrays
        if isinstance(input, np.ndarray):
            return self._format_numpy_array(input)
        
        # Handle callable objects
        if callable(input):
            return f"Function: {getattr(input, '__name__', 'Unknown')}"
        
        # Handle other objects
        return self._format_object(input)

    def _format_dict(self, data):
        """Format dictionary data for display."""
        if len(data) <= self.MAX_DICT_KEYS:
            return pformat(data, width=self.PFORMAT_WIDTH, depth=self.PFORMAT_DEPTH)
        else:
            keys_preview = list(data.keys())[:self.MAX_DICT_KEYS]
            suffix = '...' if len(data) > self.MAX_DICT_KEYS else ''
            return f"Dict with {len(data)} keys: {keys_preview}{suffix}"

    def _format_tensor(self, tensor):
        """Format tensor data for display."""
        device_info = f"Device: {tensor.device}\n" if hasattr(tensor, 'device') else ""
        min_val = float(tensor.min())
        max_val = float(tensor.max())
        
        # Check if it's an image tensor (ComfyUI format)
        if len(tensor.shape) == 4 and tensor.shape[0] >= 1:
            batch_size, height, width, channels = tensor.shape
            return (f"IMAGE: {width}×{height}×{channels} (Batch: {batch_size})\n"
                   f"Shape: {tuple(tensor.shape)}\n"
                   f"Dtype: {tensor.dtype}\n"
                   f"{device_info}"
                   f"Range: [{min_val:.4f}, {max_val:.4f}]")
        elif len(tensor.shape) == 3:
            return (f"TENSOR 3D: {tuple(tensor.shape)}\n"
                   f"Dtype: {tensor.dtype}\n"
                   f"{device_info}"
                   f"Range: [{min_val:.4f}, {max_val:.4f}]")
        else:
            return (f"TENSOR: {tuple(tensor.shape)}\n"
                   f"Dtype: {tensor.dtype}\n"
                   f"{device_info}"
                   f"Range: [{min_val:.4f}, {max_val:.4f}]")

    def _format_numpy_array(self, array):
        """Format numpy array for display."""
        min_val = float(array.min())
        max_val = float(array.max())
        return (f"NumPy Array: {array.shape}\n"
               f"Dtype: {array.dtype}\n"
               f"Range: [{min_val:.4f}, {max_val:.4f}]")

    def _format_object(self, obj):
        """Format generic object for display."""
        value_type = type(obj).__name__
        attrs = []
        
        # Try to extract useful attributes
        for attr in ['shape', 'size', 'length', '__len__']:
            if hasattr(obj, attr):
                try:
                    attr_value = getattr(obj, attr)
                    if callable(attr_value):
                        attr_value = attr_value()
                    attrs.append(f"{attr}: {attr_value}")
                except:
                    pass
        
        if attrs:
            attr_text = "\n".join(attrs)
            return f"{value_type}\n{attr_text}"
        else:
            # Try string representation with length limit
            try:
                str_repr = str(obj)
                if len(str_repr) > self.MAX_STRING_LENGTH:
                    str_repr = str_repr[:self.MAX_STRING_LENGTH] + "..."
                return str_repr
            except:
                return f"{value_type} (cannot convert to string)"
