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
                "images": ("IMAGE", {
                    "tooltip": "Input image batch or single image"
                }),
                "keep_last": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "When true, keep the last frame in the returned sequence (images_minus_last will include the last frame)"
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

    def get_last_frame(self, images, keep_last=False):
        """
        Extract the last frame from the image batch and return both the batch minus last frame and the last frame.
        
        Args:
            image: Input image tensor [batch, height, width, channels]
            keep_last: bool - if True, include the last frame in the first output sequence
        
        Returns:
            tuple: (images_minus_last, last_frame) as image tensors
        """
        try:
            # If input is not a tensor, let it raise naturally
            batch_size = images.shape[0]

            # Single image: return the same image for both outputs (preserve original behavior)
            if batch_size == 1:
                return (images, images)

            # Get the last frame (preserve batch dimension for last_frame)
            last_frame = images[-1:]

            # Decide whether to keep the last frame in the returned sequence or exclude it
            if keep_last:
                # Keep the entire original sequence (images_minus_last is effectively the original batch)
                images_minus_last = images
            else:
                # Exclude the last frame from the sequence
                images_minus_last = images[:-1]

            return (images_minus_last, last_frame)
            
        except Exception as e:
            error_msg = f"Failed to extract last frame: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)
