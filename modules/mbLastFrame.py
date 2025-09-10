"""
Last Frame Node for ComfyUI
Returns the last frame from an image batch or the single image itself.
"""

# Standard library imports
import torch

class mbLastFrame:
    """Extract the last frame from an image batch or return the single image."""
    
    def __init__(self):
        """Initialize the last frame node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for the last frame extraction."""
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image batch or single image"
                }),
            }
        }

    # Node metadata
    TITLE = "Last Frame"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "get_last_frame"
    CATEGORY = "unset"
    DESCRIPTION = "Returns the last frame from an image batch or the single image itself."

    def get_last_frame(self, image):
        """
        Extract the last frame from the image batch.
        
        Args:
            image: Input image tensor [batch, height, width, channels]
            
        Returns:
            tuple: Last frame as image tensor
        """
        try:
            # If single image (batch size 1), return as is
            if image.shape[0] == 1:
                return (image,)
            
            # For batch, return the last frame
            last_frame = image[-1:]  # Keep dimensions
            return (last_frame,)
            
        except Exception as e:
            error_msg = f"Failed to extract last frame: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)
