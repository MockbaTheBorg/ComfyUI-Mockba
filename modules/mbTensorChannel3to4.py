"""
Tensor Channel 3 to 4 Converter Node for ComfyUI
Converts a 1,x,y,3 tensor and mask to a 1,x,y,4 tensor by adding mask as alpha channel.
"""

# Standard library imports
import torch

# Local imports
from .common import any_typ

class mbTensorChannel3to4:
    """Convert a 1,x,y,3 tensor and mask to a 1,x,y,4 tensor by adding mask as alpha channel."""
    
    def __init__(self):
        """Initialize the tensor channel converter node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for tensor channel conversion."""
        return {
            "required": {
                "tensor": (any_typ, {
                    "tooltip": "Input tensor to convert (ideally 1,x,y,3 format)"
                }),
                "mask": ("MASK", {
                    "tooltip": "Mask to use as alpha channel"
                }),
            },
        }

    # Node metadata
    TITLE = "Tensor 3+Mask to 4"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("tensor",)
    FUNCTION = "convert_channels"
    CATEGORY = "unset"
    DESCRIPTION = "Convert a 1,x,y,3 tensor and mask to a 1,x,y,4 tensor by adding the mask as alpha channel. Returns unchanged if not 1,x,y,3."

    def convert_channels(self, tensor, mask):
        """
        Convert tensor from 3 channels to 4 channels by adding mask as alpha.
        
        Args:
            tensor: Input tensor to convert (should be 1,x,y,3)
            mask: Mask to use as alpha channel
            
        Returns:
            tuple: (converted_tensor,) - RGBA tensor with mask as alpha
        """
        try:
            # Check if tensor is a torch tensor
            if not isinstance(tensor, torch.Tensor):
                print(f"mbTensorChannel3to4: Input is not a torch tensor, type: {type(tensor)}")
                return (tensor,)
            
            # Check if mask is a torch tensor
            if not isinstance(mask, torch.Tensor):
                print(f"mbTensorChannel3to4: Mask is not a torch tensor, type: {type(mask)}")
                return (tensor,)
            
            # Get tensor shape
            tensor_shape = tensor.shape
            mask_shape = mask.shape
            
            # Check if tensor matches 1,x,y,3 format
            if len(tensor_shape) == 4 and tensor_shape[0] == 1 and tensor_shape[3] == 3:
                # Get spatial dimensions
                height, width = tensor_shape[1], tensor_shape[2]
                
                # Resize mask to match tensor spatial dimensions if needed
                if len(mask_shape) == 3 and mask_shape[0] == 1:
                    # Mask is 1,h,w format
                    if mask_shape[1] != height or mask_shape[2] != width:
                        # Resize mask to match tensor dimensions
                        mask_resized = torch.nn.functional.interpolate(
                            mask.unsqueeze(1),  # Add channel dim: 1,1,h,w
                            size=(height, width),
                            mode='bilinear',
                            align_corners=False
                        ).squeeze(1)  # Remove channel dim: 1,h,w
                    else:
                        mask_resized = mask
                elif len(mask_shape) == 2:
                    # Mask is h,w format, add batch dimension
                    mask_resized = mask.unsqueeze(0)  # 1,h,w
                    if mask_shape[0] != height or mask_shape[1] != width:
                        # Resize mask to match tensor dimensions
                        mask_resized = torch.nn.functional.interpolate(
                            mask_resized.unsqueeze(1),  # Add channel dim: 1,1,h,w
                            size=(height, width),
                            mode='bilinear',
                            align_corners=False
                        ).squeeze(1)  # Remove channel dim: 1,h,w
                else:
                    print(f"mbTensorChannel3to4: Unexpected mask shape {mask_shape}, creating empty alpha")
                    mask_resized = torch.zeros((1, height, width), dtype=tensor.dtype, device=tensor.device)
                
                # Ensure mask is on same device as tensor
                mask_resized = mask_resized.to(tensor.device, dtype=tensor.dtype)
                
                # Add alpha channel dimension to match tensor format (1,h,w,1)
                alpha_channel = mask_resized.unsqueeze(-1)  # 1,h,w,1
                
                # Concatenate RGB tensor with alpha channel
                converted_tensor = torch.cat([tensor, alpha_channel], dim=-1)  # 1,h,w,4
                
                print(f"mbTensorChannel3to4: Converted tensor from shape {tensor_shape} to {converted_tensor.shape}")
                return (converted_tensor,)
            else:
                # Return unchanged if not 1,x,y,3 format
                print(f"mbTensorChannel3to4: Tensor shape {tensor_shape} does not match 1,x,y,3 format, returning unchanged")
                return (tensor,)
                
        except Exception as e:
            print(f"mbTensorChannel3to4: Error processing tensor: {str(e)}")
            return (tensor,)
