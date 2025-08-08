"""
Image Subtraction Node for ComfyUI
Computes visual differences between two images with different output modes.
"""

# Standard library imports
import torch

# Local imports
from .common import CATEGORIES


class mbImageSubtract:
    """Subtract two images to visualize differences with configurable output modes."""
    
    # Class constants
    MODE_OPTIONS = ["Difference Values", "Binary Difference"]
    DEFAULT_MODE = "Difference Values"
    BINARY_THRESHOLD = 1e-6  # Threshold for binary difference detection
    
    def __init__(self):
        """Initialize the image subtraction node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for image subtraction."""
        return {
            "required": {
                "a": ("IMAGE", {
                    "tooltip": "First image (minuend)"
                }),
                "b": ("IMAGE", {
                    "tooltip": "Second image (subtrahend)"
                }),
                "mode": (cls.MODE_OPTIONS, {
                    "default": cls.DEFAULT_MODE,
                    "tooltip": "Output mode: 'Difference Values' shows actual differences, 'Binary Difference' shows white where differences exist"
                }),
            }
        }

    # Node metadata
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "subtract_images"
    CATEGORY = CATEGORIES["IMAGE_PROCESSING"]
    DESCRIPTION = (
        "Subtract two images to visualize differences. Mode options: 'Difference Values' shows actual difference values, "
        "'Binary Difference' shows black where no difference and white where differences exist."
    )

    def subtract_images(self, a, b, mode):
        """
        Subtract two images and return the difference.
        
        Args:
            a: First image tensor (minuend)
            b: Second image tensor (subtrahend)  
            mode: Output mode for difference visualization
            
        Returns:
            tuple: Difference image based on selected mode
        """
        try:
            # Calculate absolute difference
            diff = torch.abs(a - b)
            
            if mode == "Binary Difference":
                result = self._create_binary_difference(diff)
            else:  # "Difference Values"
                result = self._create_value_difference(diff)
                
            return (result,)
            
        except Exception as e:
            error_msg = f"Failed to subtract images: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)

    def _create_binary_difference(self, diff):
        """Create binary difference mask (black=no difference, white=difference)."""
        # Use threshold to account for floating point precision
        binary_diff = (diff > self.BINARY_THRESHOLD).float()
        return binary_diff

    def _create_value_difference(self, diff):
        """Create difference values clamped to valid range."""
        # Return actual difference values (clamped between 0 and 1)
        return torch.clamp(diff, 0, 1)


