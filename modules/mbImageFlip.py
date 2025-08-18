"""
Image Flip Node for ComfyUI
Flips images horizontally, vertically, or both with batch processing support.
"""

# Standard library imports
import torch

# Local imports
from .common import CATEGORIES


class mbImageFlip:
    """Flip images horizontally, vertically, or both directions."""
    
    # Class constants
    FLIP_OPTIONS = ["none", "horizontal", "vertical", "both"]
    DEFAULT_FLIP = "none"
    
    # Tensor dimension indices for ComfyUI image format [batch, height, width, channels]
    HEIGHT_DIM = 1
    WIDTH_DIM = 2
    
    def __init__(self):
        """Initialize the image flip node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for image flipping."""
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image tensor to flip"
                }),
                "flip": (cls.FLIP_OPTIONS, {
                    "default": cls.DEFAULT_FLIP,
                    "tooltip": "Direction to flip the image"
                }),
            }
        }

    # Node metadata
    TITLE = "Image Flip"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "flip_image"
    CATEGORY = CATEGORIES["IMAGE_PROCESSING"]
    DESCRIPTION = "Flip images horizontally, vertically, or both directions with batch processing support."

    def flip_image(self, image, flip):
        """
        Flip image in the specified direction.
        
        Args:
            image: Input image tensor in ComfyUI format [batch, height, width, channels]
            flip: Direction to flip ('none', 'horizontal', 'vertical', 'both')
            
        Returns:
            tuple: Flipped image tensor
        """
        if flip == "none":
            return (image,)

        try:
            # Process all images in batch efficiently
            flipped_tensor = self._apply_flip_transform(image, flip)
            return (flipped_tensor,)
            
        except Exception as e:
            error_msg = f"Failed to flip image: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)

    def _apply_flip_transform(self, image_tensor, flip_direction):
        """Apply flip transformation to the entire batch efficiently."""
        if flip_direction == "horizontal":
            return torch.flip(image_tensor, [self.WIDTH_DIM])
        elif flip_direction == "vertical":
            return torch.flip(image_tensor, [self.HEIGHT_DIM])
        elif flip_direction == "both":
            return torch.flip(image_tensor, [self.HEIGHT_DIM, self.WIDTH_DIM])
        else:
            return image_tensor
