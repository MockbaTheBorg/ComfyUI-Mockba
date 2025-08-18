"""
Image Size Display Node for ComfyUI
Shows image size information with UI feedback and passthrough functionality.
"""

# Local imports
from .common import CATEGORIES


class mbImageSize:
    """Display image size information with UI feedback."""
    
    # Tensor dimension indices for ComfyUI image format [batch, height, width, channels]
    HEIGHT_INDEX = 1
    WIDTH_INDEX = 2
    
    def __init__(self):
        """Initialize the image size display node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for image size display."""
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image tensor to analyze"
                })
            },
            "hidden": {
                "width": ("INT",),
                "height": ("INT",),
            }
        }

    # Node metadata
    TITLE = "Image Size Display"
    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("IMAGE", "width", "height")
    FUNCTION = "display_size"
    CATEGORY = "unset"
    DESCRIPTION = "Display image size information with UI feedback and passthrough functionality."
    OUTPUT_NODE = True

    def display_size(self, image, width=0, height=0):
        """
        Display image size information in UI and return dimensions.
        
        Args:
            image: Input image tensor in ComfyUI format [batch, height, width, channels]
            width: Hidden parameter for UI display (auto-populated)
            height: Hidden parameter for UI display (auto-populated)
            
        Returns:
            dict: UI update with size info and passthrough results
        """
        try:
            # Extract dimensions from image tensor
            shape = image.shape
            actual_width = shape[self.WIDTH_INDEX]
            actual_height = shape[self.HEIGHT_INDEX]
            
            return {
                "ui": {
                    "width": [actual_width], 
                    "height": [actual_height]
                },
                "result": (
                    image,
                    actual_width,
                    actual_height,
                ),
            }
            
        except Exception as e:
            error_msg = f"Failed to get image size: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)

