"""
Mask Apply Node for ComfyUI
Applies a mask to an image, returning only the masked part while keeping the image the same size.
"""

# Standard library imports
import torch

# Local imports
from .common import CATEGORIES


class mbMaskApply:
    """Apply a mask to an image, keeping only the masked parts while maintaining image size."""
    
    def __init__(self):
        """Initialize the mask apply node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for mask application."""
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image to apply mask to"
                }),
            },
            "optional": {
                "mask": ("MASK", {
                    "tooltip": "Mask to apply to the image. If None, returns original image"
                }),
                "invert_mask": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Invert the mask before applying"
                })
            }
        }

    # Node metadata
    TITLE = "Mask Apply"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "apply_mask"
    CATEGORY = "unset"
    DESCRIPTION = "Apply a mask to an image, keeping only the masked parts while maintaining the original image size. Non-masked areas become transparent/black."

    def apply_mask(self, image, mask=None, invert_mask=False):
        """
        Apply mask to image, keeping only the masked parts.
        
        Args:
            image: Input image tensor in ComfyUI format [batch, height, width, channels]
            mask: Optional mask tensor in ComfyUI format [batch, height, width]
            invert_mask: Whether to invert the mask before applying
            
        Returns:
            tuple: Masked image tensor
        """
        try:
            # If no mask provided, return original image
            if mask is None:
                print("No mask provided, returning original image")
                return (image,)
            
            # Check if mask is all zeros
            if torch.all(mask == 0):
                print("Mask is all zeros, returning original image")
                return (image,)
            
            # Apply the mask
            masked_image = self._apply_mask_to_image(image, mask, invert_mask)
            
            return (masked_image,)
            
        except Exception as e:
            print(f"Mask application failed: {str(e)}")
            # Return original image on error
            return (image,)

    def _apply_mask_to_image(self, image, mask, invert_mask):
        """
        Apply mask to image tensor.
        
        Args:
            image: Input image tensor [batch, height, width, channels]
            mask: Input mask tensor [batch, height, width]
            invert_mask: Whether to invert the mask
            
        Returns:
            torch.Tensor: Masked image tensor
        """
        # Ensure we're working with the right device
        device = image.device
        mask = mask.to(device)
        
        # Get image dimensions
        batch_size, height, width, channels = image.shape
        
        # Ensure mask has the same batch size as image
        if mask.shape[0] != batch_size:
            if mask.shape[0] == 1:
                # Broadcast mask to match image batch size
                mask = mask.repeat(batch_size, 1, 1)
            else:
                raise ValueError(f"Mask batch size ({mask.shape[0]}) doesn't match image batch size ({batch_size})")
        
        # Ensure mask has the same spatial dimensions as image
        if mask.shape[1:] != (height, width):
            # Resize mask to match image dimensions
            mask = torch.nn.functional.interpolate(
                mask.unsqueeze(1),  # Add channel dimension for interpolation
                size=(height, width),
                mode='nearest'
            ).squeeze(1)  # Remove channel dimension
        
        # Invert mask if requested
        if invert_mask:
            mask = 1.0 - mask
            print("Mask inverted")
        
        # Expand mask to match image channels
        # mask shape: [batch, height, width] -> [batch, height, width, channels]
        mask_expanded = mask.unsqueeze(-1).expand(-1, -1, -1, channels)
        
        # Apply mask to image
        # Areas where mask is 1.0 keep original image, areas where mask is 0.0 become black
        masked_image = image * mask_expanded
        
        # Calculate statistics for logging
        mask_coverage = torch.mean(mask).item()
        print(f"Applied mask with {mask_coverage:.2%} coverage")
        
        return masked_image

    @classmethod
    def IS_CHANGED(cls, image, mask=None, invert_mask=False):
        """Check if inputs have changed to determine if node needs to re-execute."""
        # Always re-execute when inputs change
        return True
