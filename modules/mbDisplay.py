import torch
import numpy as np
from pprint import pformat
from .common import any_typ

# Universal display node that shows information about any input type
class mbDisplay:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "input": (any_typ, {}),
                "value": ("STRING", {"multiline": False, "default": "Display output will appear here after execution..."}),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "display"
    CATEGORY = "🖖 Mockba/utility"
    DESCRIPTION = "Universal display node that shows information about any input type - strings, numbers, images, tensors, etc."
    OUTPUT_NODE = True

    def display(self, input, value):
        try:
            # Handle None
            if input is None:
                display_text = "None"
            
            # Handle basic types - just show the value
            elif isinstance(input, (str, int, float, bool)):
                display_text = str(input)
            
            # Handle lists and tuples - show the values
            elif isinstance(input, (list, tuple)):
                display_text = str(input)
            
            # Handle dictionaries - show the dictionary
            elif isinstance(input, dict):
                if len(input) <= 10:
                    display_text = pformat(input, width=60, depth=2)
                else:
                    display_text = f"Dict with {len(input)} keys: {list(input.keys())[:10]}{'...' if len(input) > 10 else ''}"
            
            # Handle torch tensors - show characteristics
            elif hasattr(input, 'shape') and hasattr(input, 'dtype'):
                if hasattr(input, 'device'):
                    # PyTorch tensor
                    device_info = f"Device: {input.device}\n" if hasattr(input, 'device') else ""
                    
                    # Check if it's an image tensor (ComfyUI format)
                    if len(input.shape) == 4 and input.shape[0] >= 1:
                        batch_size, height, width, channels = input.shape
                        min_val = float(input.min())
                        max_val = float(input.max())
                        display_text = (f"IMAGE: {width}×{height}×{channels} (Batch: {batch_size})\n"
                                      f"Shape: {tuple(input.shape)}\n"
                                      f"Dtype: {input.dtype}\n"
                                      f"{device_info}"
                                      f"Range: [{min_val:.4f}, {max_val:.4f}]")
                    elif len(input.shape) == 3:
                        min_val = float(input.min())
                        max_val = float(input.max())
                        display_text = (f"TENSOR 3D: {tuple(input.shape)}\n"
                                      f"Dtype: {input.dtype}\n"
                                      f"{device_info}"
                                      f"Range: [{min_val:.4f}, {max_val:.4f}]")
                    else:
                        min_val = float(input.min())
                        max_val = float(input.max())
                        display_text = (f"TENSOR: {tuple(input.shape)}\n"
                                      f"Dtype: {input.dtype}\n"
                                      f"{device_info}"
                                      f"Range: [{min_val:.4f}, {max_val:.4f}]")
                else:
                    # NumPy array or similar
                    min_val = float(input.min())
                    max_val = float(input.max())
                    display_text = (f"ARRAY: {tuple(input.shape)}\n"
                                  f"Dtype: {input.dtype}\n"
                                  f"Range: [{min_val:.4f}, {max_val:.4f}]")
            
            # Handle numpy arrays
            elif isinstance(input, np.ndarray):
                min_val = float(input.min())
                max_val = float(input.max())
                display_text = (f"NumPy Array: {input.shape}\n"
                              f"Dtype: {input.dtype}\n"
                              f"Range: [{min_val:.4f}, {max_val:.4f}]")
            
            # Handle callable objects (functions, methods)
            elif callable(input):
                display_text = f"Function: {getattr(input, '__name__', 'Unknown')}"
            
            # Handle other complex objects - show characteristics
            else:
                # Try to get some basic info about the object
                value_type = type(input).__name__
                attrs = []
                for attr in ['shape', 'size', 'length', '__len__']:
                    if hasattr(input, attr):
                        try:
                            attr_value = getattr(input, attr)
                            if callable(attr_value):
                                attr_value = attr_value()
                            attrs.append(f"{attr}: {attr_value}")
                        except:
                            pass
                
                if attrs:
                    attr_text = "\n".join(attrs)
                    display_text = f"{value_type}\n{attr_text}"
                else:
                    # Try to show string representation, but limit length
                    try:
                        str_repr = str(input)
                        if len(str_repr) > 200:
                            str_repr = str_repr[:200] + "..."
                        display_text = str_repr
                    except:
                        display_text = f"{value_type} (cannot convert to string)"
        
        except Exception as e:
            display_text = f"Error: {str(e)}"
        
        # Return the display text in the UI using the same key as the widget name
        return {"ui": {"value": [display_text]}}
