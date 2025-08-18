"""
Image Batch Creator Node for ComfyUI
Creates batches from multiple images with automatic size normalization.
"""

# Standard library imports
import torch

# ComfyUI imports
import comfy.utils

# Local imports
from .common import CATEGORIES


class mbImageBatch:
    """Create batches from multiple images with automatic size matching."""
    
    # Constants for image processing
    UPSCALE_METHOD = "lanczos"
    UPSCALE_CROP = "center"
    
    # Tensor dimension indices for ComfyUI image format [batch, height, width, channels]
    BATCH_DIM = 0
    HEIGHT_INDEX = 1
    WIDTH_INDEX = 2
    
    def __init__(self):
        """Initialize the image batch creator node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for image batching."""
        return {
            "required": {
                "image1": ("IMAGE", {
                    "tooltip": "Primary image (determines batch dimensions)"
                }),
            }
        }

    # Node metadata
    TITLE = "Image Batch Creator"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "create_image_batch"
    CATEGORY = CATEGORIES["IMAGE_PROCESSING"]
    DESCRIPTION = "Create batches from multiple images with automatic size normalization."

    def create_image_batch(self, **kwargs):
        """
        Create a batch from multiple images, resizing as needed.
        
        Args:
            **kwargs: Variable number of image inputs (image1 is required, others optional)
            
        Returns:
            tuple: Batched image tensor
        """
        try:
            # Extract primary image and additional images
            primary_image = kwargs["image1"]
            additional_images = self._extract_additional_images(kwargs)
            
            if len(additional_images) == 0:
                return (primary_image,)
            
            # Process and batch all images
            batched_image = self._process_and_batch_images(primary_image, additional_images)
            return (batched_image,)
            
        except Exception as e:
            error_msg = f"Failed to create image batch: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)

    def _extract_additional_images(self, kwargs):
        """Extract additional images from kwargs, excluding image1."""
        additional_images = []
        for key, value in kwargs.items():
            if key != "image1":
                additional_images.append(value)
        return additional_images

    def _process_and_batch_images(self, primary_image, additional_images):
        """Process and batch images, normalizing sizes to match primary image."""
        batched_image = primary_image
        target_height = primary_image.shape[self.HEIGHT_INDEX]
        target_width = primary_image.shape[self.WIDTH_INDEX]
        
        for image in additional_images:
            # Resize image if dimensions don't match
            if image.shape[1:] != primary_image.shape[1:]:
                resized_image = self._resize_image(image, target_width, target_height)
            else:
                resized_image = image
            
            # Concatenate to batch
            batched_image = torch.cat((batched_image, resized_image), dim=self.BATCH_DIM)
        
        return batched_image

    def _resize_image(self, image, target_width, target_height):
        """Resize image to match target dimensions."""
        # Move channels for ComfyUI upscale function: [batch, height, width, channels] -> [batch, channels, height, width]
        image_for_upscale = image.movedim(-1, 1)
        
        # Upscale image
        upscaled_image = comfy.utils.common_upscale(
            image_for_upscale,
            target_width,
            target_height,
            self.UPSCALE_METHOD,
            self.UPSCALE_CROP,
        )
        
        # Move channels back: [batch, channels, height, width] -> [batch, height, width, channels]
        return upscaled_image.movedim(1, -1)


