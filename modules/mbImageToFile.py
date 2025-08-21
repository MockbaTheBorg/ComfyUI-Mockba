"""
Image to File Saver Node for ComfyUI
Saves images to files with support for multiple formats and batch processing.
"""

# Standard library imports
import os
import random
from datetime import datetime

# Third-party imports
import numpy as np
from PIL import Image
try:
    import piexif
except Exception:
    piexif = None

# ComfyUI imports
import folder_paths

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
                "jpeg_quality": ("INT", {
                    "default": 95,
                    "min": 1,
                    "max": 100,
                    "tooltip": "JPEG quality (1-100). Lower values add compression artifacts that help disguise AI generation."
                }),
                # Metadata options
                "remove_ai_metadata": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Strip AI metadata (PNG text, prompts). On by default."
                }),
                "embed_exif": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Embed realistic camera EXIF (JPEG/WebP/TIFF)."
                }),
                "exif_profile": (["random_camera", "dslr_camera", "mobile_phone", "film_vintage"], {
                    "default": "random_camera",
                    "tooltip": "Choose a camera profile for EXIF when embedding."
                }),
            },
        }

    # Node metadata
    TITLE = "Image to File Saver"
    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("image", "count")
    FUNCTION = "save_image_to_file"
    CATEGORY = "unset"
    DESCRIPTION = "Save images to files with support for multiple formats (PNG, JPEG, WebP, BMP, TIFF) and batch processing."
    OUTPUT_NODE = True

    def save_image_to_file(self, image, filename, format, save_mode, jpeg_quality, remove_ai_metadata, embed_exif, exif_profile):
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
                count = self._save_single_image(image, filename, file_extension, format, output_dir, jpeg_quality, remove_ai_metadata, embed_exif, exif_profile)
            else:  # batch mode
                count = self._save_batch_images(image, filename, file_extension, format, output_dir, jpeg_quality, remove_ai_metadata, embed_exif, exif_profile)
            
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

    def _save_single_image(self, image, base_filename, extension, format, output_dir, jpeg_quality, remove_ai_metadata, embed_exif, exif_profile):
        """Save a single image (or first image from batch)."""
        # Use first image if batch
        img_tensor = image[0] if image.shape[0] > 1 else image.squeeze(0)
        
        # Generate filename
        filename = self._generate_filename(base_filename, extension)
        filepath = output_dir + filename
        
        # Save image
        self._save_image_tensor(img_tensor, filepath, format, jpeg_quality, remove_ai_metadata, embed_exif, exif_profile)
        
        return 1

    def _save_batch_images(self, image, base_filename, extension, format, output_dir, jpeg_quality, remove_ai_metadata, embed_exif, exif_profile):
        """Save multiple images from batch with numbered filenames."""
        count = 0
        
        for i, img_tensor in enumerate(image):
            # Generate numbered filename
            numbered_filename = f"{base_filename}_{i}{extension}"
            filepath = output_dir + numbered_filename
            
            # Save image
            try:
                self._save_image_tensor(img_tensor, filepath, format, jpeg_quality, remove_ai_metadata, embed_exif, exif_profile)
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

    def _save_image_tensor(self, img_tensor, filepath, format, jpeg_quality, remove_ai_metadata, embed_exif, exif_profile):
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
        save_kwargs = self._get_save_kwargs(format, jpeg_quality)

        # PNG metadata stripping: default behavior adds nothing; ensure no pnginfo when remove_ai_metadata
        if format == "PNG":
            if remove_ai_metadata:
                image_pil.save(filepath, format=format, **save_kwargs)
            else:
                image_pil.save(filepath, format=format, **save_kwargs)
        else:
            # EXIF embedding for JPEG/WebP/TIFF if requested and library available
            if embed_exif and piexif is not None and format in ("JPEG", "WebP", "TIFF"):
                exif_bytes = self._build_exif_bytes(exif_profile)
                if exif_bytes:
                    # Pillow expects 'exif' bytes param
                    save_kwargs["exif"] = exif_bytes
            image_pil.save(filepath, format=format, **save_kwargs)
        
        print(f"Image saved: {filepath}")

    def _get_save_kwargs(self, format, jpeg_quality=95):
        """Get format-specific save parameters."""
        if format == "JPEG":
            return {"quality": max(1, min(100, jpeg_quality)), "optimize": True}
        elif format == "WebP":
            return {"quality": self.WEBP_QUALITY, "method": 6}
        elif format == "PNG":
            return {"optimize": True}
        elif format == "TIFF":
            return {"compression": "lzw"}
        else:
            return {}

    # ------------------------ EXIF helpers ------------------------
    def _build_exif_bytes(self, profile: str):
        """Build EXIF bytes using a realistic camera profile. Returns None if piexif missing."""
        if piexif is None:
            print("piexif not available; skipping EXIF embedding")
            return None

        profiles = self._exif_profiles()
        if profile == "random_camera":
            profile = random.choice(list(profiles.keys()))
        data = profiles.get(profile)
        if not data:
            return None

        now_str = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
        make, model, lens, fl, fnum, iso, exp = (
            data["make"], data["model"], data["lens"], data["focal_length"], data["f_number"], data["iso"], data["exposure_time"]
        )

        zeroth_ifd = {
            piexif.ImageIFD.Make: make,
            piexif.ImageIFD.Model: model,
            piexif.ImageIFD.Software: data.get("software", "Adobe Lightroom Classic 13.0"),
            piexif.ImageIFD.DateTime: now_str,
        }
        exif_ifd = {
            piexif.ExifIFD.ExposureTime: self._to_rational(exp),
            piexif.ExifIFD.FNumber: self._to_rational(fnum),
            piexif.ExifIFD.ISOSpeedRatings: int(iso),
            piexif.ExifIFD.LensModel: lens,
            piexif.ExifIFD.FocalLength: self._to_rational(fl),
            piexif.ExifIFD.DateTimeOriginal: now_str,
            piexif.ExifIFD.DateTimeDigitized: now_str,
        }
        exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": {}, "1st": {}}
        return piexif.dump(exif_dict)

    def _to_rational(self, value):
        """Convert float to rational tuple for EXIF."""
        try:
            from fractions import Fraction
            frac = Fraction(value).limit_denominator(10000)
            return (frac.numerator, frac.denominator)
        except Exception:
            return (int(value * 100), 100)

    def _exif_profiles(self):
        """Predefined camera profiles for EXIF embedding."""
        return {
            "dslr_camera": {
                "make": "Canon",
                "model": "EOS 5D Mark IV",
                "lens": "EF24-70mm f/2.8L II USM",
                "focal_length": 50.0,
                "f_number": 4.0,
                "iso": 200,
                "exposure_time": 1/125,
                "software": "Adobe Lightroom Classic 13.0",
            },
            "mobile_phone": {
                "make": "Apple",
                "model": "iPhone 14 Pro",
                "lens": "iPhone 14 Pro back triple camera 6.86mm f/1.78",
                "focal_length": 6.86,
                "f_number": 1.78,
                "iso": 80,
                "exposure_time": 1/120,
                "software": "16.6",
            },
            "film_vintage": {
                "make": "Nikon",
                "model": "FM2 (digitized)",
                "lens": "AI-S 50mm f/1.8",
                "focal_length": 50.0,
                "f_number": 5.6,
                "iso": 400,
                "exposure_time": 1/250,
                "software": "Adobe Photoshop CS6",
            },
        }