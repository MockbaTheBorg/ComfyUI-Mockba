"""
Tensor Channel 4 to 3 Converter Node for ComfyUI
Converts a 1,x,y,4 tensor to a 1,x,y,3 tensor by removing the alpha channel.
Does nothing if the tensor is not in 1,x,y,4 format.
"""

# Standard library imports
import torch

# Local imports
from .common import any_typ, CATEGORIES


class mbTensorChannel4to3:
    """Convert a 1,x,y,4 tensor to a 1,x,y,3 tensor by removing the alpha channel."""
    
    def __init__(self):
        """Initialize the tensor channel converter node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for tensor channel conversion."""
        return {
            "required": {
                "tensor": (any_typ, {
                    "tooltip": "Input tensor to convert (ideally 1,x,y,4 format)"
                }),
            },
        }

    # Node metadata
    TITLE = "Tensor Channel Converter"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("tensor",)
    FUNCTION = "convert_channels"
    CATEGORY = CATEGORIES["DATA_MANAGEMENT"]
    DESCRIPTION = "Convert a 1,x,y,4 tensor to a 1,x,y,3 tensor by removing the alpha channel. Returns unchanged if not 1,x,y,4."

    def convert_channels(self, tensor):
        """
        Convert tensor from 4 channels to 3 channels if it matches 1,x,y,4 format.
        
        Args:
            tensor: Input tensor to convert
            
        Returns:
            tuple: (converted_tensor,) - Either converted 1,x,y,3 tensor or original tensor unchanged
        """
        try:
            # Check if tensor is a torch tensor
            if not isinstance(tensor, torch.Tensor):
                print(f"mbTensorChannel4to3: Input is not a torch tensor, type: {type(tensor)}")
                return (tensor,)
            
            # Get tensor shape
            shape = tensor.shape
            
            # Check if tensor matches 1,x,y,4 format
            if len(shape) == 4 and shape[0] == 1 and shape[3] == 4:
                # Convert from 1,x,y,4 to 1,x,y,3 by taking only RGB channels (ignoring alpha)
                converted_tensor = tensor[:, :, :, :3]
                print(f"mbTensorChannel4to3: Converted tensor from shape {shape} to {converted_tensor.shape}")
                return (converted_tensor,)
            else:
                # Return unchanged if not 1,x,y,4 format
                print(f"mbTensorChannel4to3: Tensor shape {shape} does not match 1,x,y,4 format, returning unchanged")
                return (tensor,)
                
        except Exception as e:
            print(f"mbTensorChannel4to3: Error processing tensor: {str(e)}")
            return (tensor,)
