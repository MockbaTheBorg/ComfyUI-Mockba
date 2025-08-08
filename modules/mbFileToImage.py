"""
File to Image Loader Node for ComfyUI
Loads images from files with support for single images and batch loading.
"""

# Standard library imports
import os

# Third-party imports
import torch
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont

# ComfyUI imports
import folder_paths

# Local imports
from .common import CATEGORIES, create_text_image, convert_pil_to_tensor


class mbFileToImage:
    """Load images from files with automatic format handling and batch support."""
    
    # Class constants
    DEFAULT_FILENAME = "image"
    SUPPORTED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]
    DEFAULT_EXTENSION = ".png"
    
    # Default image dimensions for fallback
    DEFAULT_WIDTH = 512
    DEFAULT_HEIGHT = 512
    DEFAULT_CHANNELS = 3
    
    # Image processing constants
    IMAGE_NORMALIZE_FACTOR = 255.0
    
    def __init__(self):
        """Initialize the file to image loader node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for image file loading."""
        return {
            "required": {
                "filename": ("STRING", {
                    "default": cls.DEFAULT_FILENAME,
                    "tooltip": "Base filename for image(s) to load (extension optional)"
                }),
                "load_mode": (["single", "batch"], {
                    "default": "single",
                    "tooltip": "Single: load one image, Batch: load sequentially numbered images"
                }),
            }
        }

    # Node metadata
    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("image", "count")
    FUNCTION = "load_image_from_file"
    CATEGORY = CATEGORIES["FILE_OPS"]
    DESCRIPTION = "Load images from files with support for single images and batch loading of sequentially numbered files. Returns error image with message if file not found."

    def load_image_from_file(self, filename, load_mode):
        """
        Load image(s) from file(s).
        
        Args:
            filename: Base filename for image(s) to load
            load_mode: "single" for one image, "batch" for multiple numbered images
            
        Returns:
            tuple: (image_tensor, count) where count is number of images loaded
        """
        try:
            if load_mode == "single":
                image_tensor, count = self._load_single_image(filename)
            else:  # batch mode
                image_tensor, count = self._load_batch_images(filename)
            
            return (image_tensor, count)
            
        except Exception as e:
            error_msg = f"Failed to load image from file: {str(e)}"
            print(error_msg)
            # Return error image with message
            error_image = self._create_error_image(error_msg)
            return (error_image, 0)

    def _load_single_image(self, base_filename):
        """Load a single image file."""
        filepath = self._find_image_file(base_filename)
        
        if filepath is None:
            error_msg = f"Image file not found: {base_filename}"
            print(error_msg)
            error_image = self._create_error_image(error_msg)
            return error_image, 0
        
        try:
            image_tensor = self._load_and_process_image(filepath)
            return image_tensor, 1
        except Exception as e:
            error_msg = f"Error loading image {filepath}: {str(e)}"
            print(error_msg)
            error_image = self._create_error_image(error_msg)
            return error_image, 0

    def _load_batch_images(self, base_filename):
        """Load multiple sequentially numbered images."""
        images = []
        i = 0
        
        while True:
            numbered_filename = f"{base_filename}_{i}"
            filepath = self._find_image_file(numbered_filename)
            
            if filepath is None:
                break
                
            try:
                image_tensor = self._load_and_process_image(filepath)
                images.append(image_tensor)
                i += 1
            except Exception as e:
                print(f"Error loading image {filepath}: {str(e)}")
                break
        
        if len(images) == 0:
            error_msg = f"No batch images found for: {base_filename}_*"
            print(error_msg)
            error_image = self._create_error_image(error_msg)
            return error_image, 0
        
        # Concatenate all images into batch
        batch_tensor = torch.cat(images, dim=0)
        return batch_tensor, len(images)

    def _find_image_file(self, base_filename):
        """Find image file with supported extension."""
        input_dir = folder_paths.get_input_directory().replace("\\", "/") + "/"
        
        # If filename already has extension, try it directly
        if any(base_filename.lower().endswith(ext) for ext in self.SUPPORTED_EXTENSIONS):
            filepath = input_dir + base_filename
            if os.path.exists(filepath):
                return filepath
        else:
            # Try with each supported extension
            for ext in self.SUPPORTED_EXTENSIONS:
                filepath = input_dir + base_filename + ext
                if os.path.exists(filepath):
                    return filepath
        
        return None

    def _load_and_process_image(self, filepath):
        """Load and process image file into ComfyUI tensor format."""
        # Load image and convert to RGB
        image_pil = Image.open(filepath)
        image_pil = ImageOps.exif_transpose(image_pil)  # Handle EXIF rotation
        image_pil = image_pil.convert("RGB")
        
        # Convert to numpy array and normalize
        image_np = np.array(image_pil).astype(np.float32) / self.IMAGE_NORMALIZE_FACTOR
        
        # Convert to tensor in ComfyUI format [batch, height, width, channels]
        image_tensor = torch.from_numpy(image_np).unsqueeze(0)
        
        return image_tensor

    def _create_error_image(self, error_message, width=512, height=512):
        """
        Create a black and white error image with the error message using global utilities.
        
        Args:
            error_message: The error message to display
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            torch.Tensor: Error image tensor in ComfyUI format
        """
        # Use the global text image creation function
        img = create_text_image(error_message, font_size=20, margin=20, max_width=width, min_width=min(width, 200))
        
        # If the generated image is different size than requested, resize or recreate
        if img.size != (width, height):
            # If it's a different size, let's stick with the auto-sized version
            # or we could resize it to fit the requested dimensions
            pass
        
        # Convert to ComfyUI tensor format using global function
        image_tensor = convert_pil_to_tensor(img)
        
        return image_tensor

    def _create_fallback_image(self):
        """Create a default fallback image when loading fails."""
        fallback_tensor = torch.zeros(
            1, self.DEFAULT_HEIGHT, self.DEFAULT_WIDTH, self.DEFAULT_CHANNELS
        )
        return fallback_tensor
