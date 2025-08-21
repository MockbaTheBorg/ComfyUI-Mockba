"""
Enhanced Image Loader Node for ComfyUI
Loads images from files with support for multiple formats, subfolders, and advanced processing options.
"""

# Standard library imports
import os

# Third-party imports
import numpy as np
import torch
from PIL import Image

# ComfyUI imports
import folder_paths

class mbImageLoad:
    """Load images from files with multi-format support, subfolder scanning, and alpha channel handling."""
    
    # Class constants
    SUPPORTED_FORMATS = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif"]
    EXCLUDE_FOLDERS = ["clipspace", "__pycache__", ".git", "temp"]
    
    # Image processing constants
    IMAGE_NORMALIZE_FACTOR = 255.0
    DEFAULT_MASK_SIZE = (64, 64)
    
    def __init__(self):
        """Initialize the image loader node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for image loading with dynamic file discovery."""
        try:
            file_list = cls._discover_image_files()
            
            return {
                "required": {
                    "image": (sorted(file_list), {
                        "image_upload": True,
                        "tooltip": "Select image file to load (supports subfolders)"
                    })
                },
                "optional": {
                    "force_rgb": ("BOOLEAN", {
                        "default": True,
                        "tooltip": "Force conversion to RGB (disable for grayscale preservation)"
                    })
                }
            }
        except Exception as e:
            print(f"Error discovering image files: {str(e)}")
            return {
                "required": {
                    "image": ([], {"image_upload": True})
                }
            }

    # Node metadata
    TITLE = "Image Loader"
    RETURN_TYPES = ("IMAGE", "MASK", "STRING", "INT", "INT")
    RETURN_NAMES = ("image", "mask", "filename", "width", "height")
    FUNCTION = "load_image_enhanced"
    CATEGORY = "unset"
    DESCRIPTION = "Load images with support for multiple formats (PNG, JPG, WebP, BMP, TIFF), subfolders, and alpha channel extraction."

    def load_image_enhanced(self, image, force_rgb=True):
        """
        Load and process image file with enhanced options.
        
        Args:
            image: Selected image filename
            force_rgb: Whether to force RGB conversion
            
        Returns:
            tuple: (image_tensor, mask_tensor, filename, width, height)
        """
        try:
            # Get full image path
            image_path = folder_paths.get_annotated_filepath(image)
            if not image_path or not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image}")
            
            # Load image
            pil_image = Image.open(image_path)
            original_size = pil_image.size
            
            # Process image and extract mask
            image_tensor, mask_tensor = self._process_image(pil_image, force_rgb)
            
            # Get filename without path
            filename = os.path.basename(image_path)
            
            print(f"Loaded image: {filename} ({original_size[0]}x{original_size[1]})")
            
            return (image_tensor, mask_tensor, filename, original_size[0], original_size[1])
            
        except Exception as e:
            error_msg = f"Failed to load image: {str(e)}"
            print(error_msg)
            # Return safe fallback
            fallback_image = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
            fallback_mask = torch.zeros((1, 64, 64), dtype=torch.float32)
            return (fallback_image, fallback_mask, "error", 64, 64)

    @classmethod
    def _discover_image_files(cls):
        """Discover all supported image files in the input directory and subfolders."""
        input_dir = folder_paths.get_input_directory()
        file_list = []
        
        try:
            for root, dirs, files in os.walk(input_dir):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if d not in cls.EXCLUDE_FOLDERS]
                
                for file in files:
                    if cls._is_supported_image_format(file):
                        file_path = os.path.relpath(os.path.join(root, file), start=input_dir)
                        file_path = file_path.replace("\\", "/")
                        file_list.append(file_path)
        except Exception as e:
            print(f"Error scanning directory {input_dir}: {str(e)}")
        
        return file_list

    @classmethod
    def _is_supported_image_format(cls, filename):
        """Check if the file has a supported image format extension."""
        file_ext = os.path.splitext(filename.lower())[1]
        return file_ext in cls.SUPPORTED_FORMATS

    def _process_image(self, pil_image, force_rgb):
        """
        Process PIL image into tensor format and extract alpha mask.
        
        Args:
            pil_image: PIL Image object
            force_rgb: Whether to force RGB conversion
            
        Returns:
            tuple: (image_tensor, mask_tensor)
        """
        # Extract alpha channel if it exists
        alpha_channel = None
        if "A" in pil_image.getbands():
            alpha_channel = pil_image.getchannel("A")

        # Prepare image for tensor conversion
        if pil_image.mode == 'L' and not force_rgb:
            # Keep it as grayscale, will be expanded to 3 channels later
            image_for_tensor = pil_image
        else:
            # Convert to RGB for all other cases
            image_for_tensor = pil_image.convert("RGB")

        # Convert to numpy array and normalize
        image_array = np.array(image_for_tensor).astype(np.float32) / self.IMAGE_NORMALIZE_FACTOR
        
        # Handle grayscale images
        if len(image_array.shape) == 2:
            image_array = np.stack([image_array] * 3, axis=-1)
        
        # Convert to tensor with batch dimension
        image_tensor = torch.from_numpy(image_array).unsqueeze(0)
        
        # Process alpha mask
        if alpha_channel is not None:
            mask_array = np.array(alpha_channel).astype(np.float32) / self.IMAGE_NORMALIZE_FACTOR
            # Invert mask (ComfyUI convention: 0 = masked, 1 = unmasked)
            mask_tensor = torch.from_numpy(1.0 - mask_array).unsqueeze(0)
        else:
            # Create empty mask with same dimensions as image
            height, width = image_array.shape[:2]
            mask_tensor = torch.zeros((1, height, width), dtype=torch.float32)
        
        return image_tensor, mask_tensor

    @classmethod
    def IS_CHANGED(cls, image, **kwargs):
        """Check if the image file has changed using SHA256 hash."""
        try:
            image_path = folder_paths.get_annotated_filepath(image)
            if not image_path or not os.path.exists(image_path):
                return "file_not_found"
            
            # Use file modification time and size for faster checks
            stat = os.stat(image_path)
            return f"{stat.st_mtime}_{stat.st_size}"
            
        except Exception as e:
            print(f"Error checking file change: {str(e)}")
            return "error"

    @classmethod
    def VALIDATE_INPUTS(cls, image, **kwargs):
        """Validate that the selected image file exists and is readable."""
        try:
            image_path = folder_paths.get_annotated_filepath(image)
            
            if not image_path:
                return f"Invalid image file path: {image}"
            
            if not os.path.exists(image_path):
                return f"Image file does not exist: {image_path}"
            
            if not cls._is_supported_image_format(image_path):
                return f"Unsupported image format: {image_path}"
            
            # Try to open the image to ensure it's valid
            try:
                with Image.open(image_path) as test_image:
                    test_image.verify()
            except Exception as e:
                return f"Invalid or corrupted image file: {str(e)}"
            
            return True
            
        except Exception as e:
            return f"Validation error: {str(e)}"


