"""
Last Frame Node for ComfyUI
Returns the image batch minus the last frame and the last frame separately.
If a single image is passed, both outputs contain the same image.
"""

# Standard library imports
import torch

class mbLastFrame:
    """Extract the last frame from an image batch and return both the batch minus last frame and the last frame separately."""
    
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
    TITLE = "Image Last Frame"
    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("images_minus_last", "last_frame")
    FUNCTION = "get_last_frame"
    CATEGORY = "unset"
    DESCRIPTION = "Returns the image batch minus the last frame and the last frame separately. If single image, both outputs are the same."

    def get_last_frame(self, image):
        """
        Extract the last frame from the image batch and return both the batch minus last frame and the last frame.
        
        Args:
            image: Input image tensor [batch, height, width, channels]
            
        Returns:
            tuple: (images_minus_last, last_frame) as image tensors
        """
        try:
            # If single image (batch size 1), return the same image for both outputs
            if image.shape[0] == 1:
                return (image, image)
            
            # For batch, return all frames except the last, and the last frame
            images_minus_last = image[:-1]  # All frames except the last
            last_frame = image[-1:]  # Keep dimensions for the last frame
            return (images_minus_last, last_frame)
            
        except Exception as e:
            error_msg = f"Failed to extract last frame: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)
