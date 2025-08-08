"""
Image to File Saver Node for ComfyUI
Saves images to files with support for multiple formats and batch processing.
"""

# Standard library imports
import os

# Third-party imports
import numpy as np
from PIL import Image

# ComfyUI imports
import folder_paths

# Local imports
from .common import CATEGORIES


class mbImageToFile:
    """Save images to files with automatic format detection and batch support."""
    
    # Class constants
    DEFAULT_FILENAME = "image"
    SUPPORTED_FORMATS = ["PNG", "JPEG", "WebP", "BMP", "TIFF"]
    DEFAULT_FORMAT = "PNG"
    
    # Quality settings for different formats
    JPEG_QUALITY = 95
    WEBP_QUALITY = 95
    
    # Image processing constants
    IMAGE_DENORMALIZE_FACTOR = 255.0
    
    def __init__(self):
        """Initialize the image to file saver node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for image file saving."""
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image tensor to save"
                }),
                "filename": ("STRING", {
                    "default": cls.DEFAULT_FILENAME,
                    "tooltip": "Base filename for saved image(s) (extension optional)"
                }),
                "format": (cls.SUPPORTED_FORMATS, {
                    "default": cls.DEFAULT_FORMAT,
                    "tooltip": "Output image format"
                }),
                "save_mode": (["single", "batch"], {
                    "default": "single",
                    "tooltip": "Single: save as one file, Batch: save each image separately with numbers"
                }),
            },
        }

    # Node metadata
    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("image", "count")
    FUNCTION = "save_image_to_file"
    CATEGORY = CATEGORIES["FILE_OPS"]
    DESCRIPTION = "Save images to files with support for multiple formats (PNG, JPEG, WebP, BMP, TIFF) and batch processing."

    def save_image_to_file(self, image, filename, format, save_mode):
        """
        Save image(s) to file(s).
        
        Args:
            image: Input image tensor in ComfyUI format [batch, height, width, channels]
            filename: Base filename for saved image(s)
            format: Output image format (PNG, JPEG, WebP, BMP, TIFF)
            save_mode: "single" for one file, "batch" for numbered files
            
        Returns:
            tuple: (original_image, count_of_saved_images)
        """
        try:
            # Prepare output directory
            output_dir = self._prepare_output_directory()
            
            # Determine file extension
            file_extension = self._get_file_extension(format)
            
            # Save images based on mode
            if save_mode == "single" or image.shape[0] == 1:
                count = self._save_single_image(image, filename, file_extension, format, output_dir)
            else:  # batch mode
                count = self._save_batch_images(image, filename, file_extension, format, output_dir)
            
            return (image, count)
            
        except Exception as e:
            error_msg = f"Failed to save image to file: {str(e)}"
            print(error_msg)
            return (image, 0)

    def _prepare_output_directory(self):
        """Prepare output directory for saving images."""
        output_dir = folder_paths.get_input_directory().replace("\\", "/") + "/"
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def _get_file_extension(self, format):
        """Get appropriate file extension for the format."""
        extension_map = {
            "PNG": ".png",
            "JPEG": ".jpg",
            "WebP": ".webp",
            "BMP": ".bmp",
            "TIFF": ".tiff"
        }
        return extension_map.get(format, ".png")

    def _save_single_image(self, image, base_filename, extension, format, output_dir):
        """Save a single image (or first image from batch)."""
        # Use first image if batch
        img_tensor = image[0] if image.shape[0] > 1 else image.squeeze(0)
        
        # Generate filename
        filename = self._generate_filename(base_filename, extension)
        filepath = output_dir + filename
        
        # Save image
        self._save_image_tensor(img_tensor, filepath, format)
        
        return 1

    def _save_batch_images(self, image, base_filename, extension, format, output_dir):
        """Save multiple images from batch with numbered filenames."""
        count = 0
        
        for i, img_tensor in enumerate(image):
            # Generate numbered filename
            numbered_filename = f"{base_filename}_{i}{extension}"
            filepath = output_dir + numbered_filename
            
            # Save image
            try:
                self._save_image_tensor(img_tensor, filepath, format)
                count += 1
            except Exception as e:
                print(f"Error saving image {numbered_filename}: {str(e)}")
                break
        
        return count

    def _generate_filename(self, base_filename, extension):
        """Generate final filename with proper extension."""
        # Remove existing extension if present
        for fmt in self.SUPPORTED_FORMATS:
            fmt_ext = self._get_file_extension(fmt)
            if base_filename.lower().endswith(fmt_ext):
                base_filename = base_filename[:-len(fmt_ext)]
                break
        
        return base_filename + extension

    def _save_image_tensor(self, img_tensor, filepath, format):
        """Convert tensor to PIL image and save with specified format."""
        # Convert tensor to numpy array and denormalize
        image_np = (self.IMAGE_DENORMALIZE_FACTOR * img_tensor.cpu().numpy()).astype(np.uint8)
        
        # Create PIL image
        if len(image_np.shape) == 3 and image_np.shape[2] == 3:
            # RGB image
            image_pil = Image.fromarray(image_np, 'RGB')
        elif len(image_np.shape) == 3 and image_np.shape[2] == 4:
            # RGBA image
            image_pil = Image.fromarray(image_np, 'RGBA')
        elif len(image_np.shape) == 2:
            # Grayscale image
            image_pil = Image.fromarray(image_np, 'L')
        else:
            # Fallback to RGB
            if len(image_np.shape) == 3:
                image_np = image_np[:, :, :3]
            image_pil = Image.fromarray(image_np, 'RGB')
        
        # Save with format-specific options
        save_kwargs = self._get_save_kwargs(format)
        image_pil.save(filepath, format=format, **save_kwargs)
        
        print(f"Image saved: {filepath}")

    def _get_save_kwargs(self, format):
        """Get format-specific save parameters."""
        if format == "JPEG":
            return {"quality": self.JPEG_QUALITY, "optimize": True}
        elif format == "WebP":
            return {"quality": self.WEBP_QUALITY, "method": 6}
        elif format == "PNG":
            return {"optimize": True}
        elif format == "TIFF":
            return {"compression": "lzw"}
        else:
            return {}