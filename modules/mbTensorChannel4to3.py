"""
Tensor Channel 4 to 3 Converter Node for ComfyUI
Converts a 1,x,y,4 tensor to a 1,x,y,3 tensor and extracts alpha as mask.
"""

# Standard library imports
import torch

# Local imports
from .common import any_typ

class mbTensorChannel4to3:
    """Convert a 1,x,y,4 tensor to a 1,x,y,3 tensor and extract alpha channel as mask."""
    
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
    TITLE = "Tensor 4 to 3+Mask"
    RETURN_TYPES = (any_typ, "MASK")
    RETURN_NAMES = ("tensor", "mask")
    FUNCTION = "convert_channels"
    CATEGORY = "unset"
    DESCRIPTION = "Convert a 1,x,y,4 tensor to a 1,x,y,3 tensor and extract the alpha channel as a mask. Returns unchanged tensor and empty mask if not 1,x,y,4."

    def convert_channels(self, tensor):
        """
        Convert tensor from 4 channels to 3 channels and extract alpha as mask.
        
        Args:
            tensor: Input tensor to convert
            
        Returns:
            tuple: (converted_tensor, mask) - RGB tensor and alpha mask
        """
        try:
            # Check if tensor is a torch tensor
            if not isinstance(tensor, torch.Tensor):
                print(f"mbTensorChannel4to3: Input is not a torch tensor, type: {type(tensor)}")
                # Create empty mask with default size
                empty_mask = torch.zeros((1, 64, 64), dtype=torch.float32)
                return (tensor, empty_mask)
            
            # Get tensor shape
            shape = tensor.shape
            
            # Check if tensor matches 1,x,y,4 format
            if len(shape) == 4 and shape[0] == 1 and shape[3] == 4:
                # Convert from 1,x,y,4 to 1,x,y,3 by taking only RGB channels
                converted_tensor = tensor[:, :, :, :3]
                
                # Extract alpha channel as mask (shape: 1,x,y)
                alpha_mask = tensor[:, :, :, 3]  # Extract alpha channel
                
                print(f"mbTensorChannel4to3: Converted tensor from shape {shape} to {converted_tensor.shape}, extracted mask shape {alpha_mask.shape}")
                return (converted_tensor, alpha_mask)
            else:
                # Return unchanged tensor and create empty mask with same spatial dimensions
                if len(shape) >= 3:
                    # Use tensor's spatial dimensions for empty mask
                    height = shape[-3] if len(shape) >= 3 else 64
                    width = shape[-2] if len(shape) >= 2 else 64
                    empty_mask = torch.zeros((1, height, width), dtype=torch.float32, device=tensor.device)
                else:
                    empty_mask = torch.zeros((1, 64, 64), dtype=torch.float32)
                
                print(f"mbTensorChannel4to3: Tensor shape {shape} does not match 1,x,y,4 format, returning unchanged with empty mask")
                return (tensor, empty_mask)
                
        except Exception as e:
            print(f"mbTensorChannel4to3: Error processing tensor: {str(e)}")
            # Create empty mask with default size
            empty_mask = torch.zeros((1, 64, 64), dtype=torch.float32)
            return (tensor, empty_mask)
