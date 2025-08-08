"""
Image Rotation Node for ComfyUI
Rotates images by 90, 180, or 270 degrees counterclockwise with batch processing.
"""

# Standard library imports
import torch

# Local imports
from .common import CATEGORIES


class mbImageRotate:
    """Rotate images by 90, 180, or 270 degrees counterclockwise."""
    
    # Class constants
    ROTATION_OPTIONS = ["0", "90", "180", "270"]
    DEFAULT_ROTATION = "0"
    
    # Rotation parameters for torch.rot90
    ROTATION_MAP = {
        "90": 1,    # 90 degrees CCW
        "180": 2,   # 180 degrees  
        "270": 3,   # 270 degrees CCW
    }
    
    # Tensor dimensions for rotation [height, width]
    ROTATION_DIMS = [1, 2]
    
    def __init__(self):
        """Initialize the image rotation node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for image rotation."""
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image tensor to rotate"
                }),
                "degrees": (cls.ROTATION_OPTIONS, {
                    "default": cls.DEFAULT_ROTATION,
                    "tooltip": "Rotation angle in degrees (counterclockwise)"
                }),
            }
        }

    # Node metadata
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "rotate_image"
    CATEGORY = CATEGORIES["IMAGE_PROCESSING"]
    DESCRIPTION = "Rotate images by 90, 180, or 270 degrees counterclockwise with efficient batch processing."

    def rotate_image(self, image, degrees):
        """
        Rotate image by specified degrees.
        
        Args:
            image: Input image tensor in ComfyUI format [batch, height, width, channels]
            degrees: Rotation angle as string ('0', '90', '180', '270')
            
        Returns:
            tuple: Rotated image tensor
        """
        if degrees == "0":
            return (image,)

        try:
            # Apply rotation to entire batch efficiently
            rotated_tensor = self._apply_rotation_transform(image, degrees)
            return (rotated_tensor,)
            
        except Exception as e:
            error_msg = f"Failed to rotate image: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)

    def _apply_rotation_transform(self, image_tensor, rotation_degrees):
        """Apply rotation transformation to the entire batch efficiently."""
        if rotation_degrees in self.ROTATION_MAP:
            k = self.ROTATION_MAP[rotation_degrees]
            return torch.rot90(image_tensor, k, self.ROTATION_DIMS)
        else:
            return image_tensor


