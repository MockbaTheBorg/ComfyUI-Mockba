"""
Image Dimensions Node for ComfyUI
Extracts width and height dimensions from image tensors.
"""

# Local imports
from .common import CATEGORIES


class mbImageDimensions:
    """Extract width and height dimensions from image tensors."""
    
    # Tensor dimension indices for ComfyUI image format [batch, height, width, channels]
    HEIGHT_INDEX = 1
    WIDTH_INDEX = 2
    
    def __init__(self):
        """Initialize the image dimensions node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for dimension extraction."""
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image tensor to measure"
                }),
            },
        }

    # Node metadata
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "get_dimensions"
    CATEGORY = CATEGORIES["IMAGE_PROCESSING"]
    DESCRIPTION = "Extract width and height dimensions from image tensors."

    def get_dimensions(self, image):
        """
        Extract image dimensions from tensor.
        
        Args:
            image: Input image tensor in ComfyUI format [batch, height, width, channels]
            
        Returns:
            tuple: (width, height) as integers
        """
        try:
            image_size = image.size()
            width = int(image_size[self.WIDTH_INDEX])
            height = int(image_size[self.HEIGHT_INDEX])
            
            return (width, height)
            
        except Exception as e:
            error_msg = f"Failed to get image dimensions: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)


