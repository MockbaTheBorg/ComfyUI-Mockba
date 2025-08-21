"""
Advanced Image Dithering Node for ComfyUI
Converts images to dithered output using various professional algorithms including error diffusion,
ordered dithering, and halftone patterns with support for both monochrome and color modes.
"""

# Third-party imports
import numpy as np
import torch

class mbImageDither:
    """Apply professional dithering algorithms to images with extensive method and parameter control."""
    
    # Class constants
    DITHERING_METHODS = [
        "Floyd-Steinberg", "Jarvis-Judice-Ninke", "Stucki", "Atkinson",
        "Bayer 2x2", "Bayer 4x4", "Bayer 8x8",
        "Halftone", "Newspaper", "Magazine", 
        "Random", "None (Threshold)"
    ]
    
    COLOR_MODES = ["Black & White", "Color"]
    
    # Default values
    DEFAULT_METHOD = "Floyd-Steinberg"
    DEFAULT_COLOR_MODE = "Black & White"
    DEFAULT_THRESHOLD = 0.5
    DEFAULT_DOT_SIZE = 4
    
    # Processing constants
    GRAYSCALE_WEIGHTS = [0.299, 0.587, 0.114]  # Standard RGB to grayscale conversion
    
    # Halftone screen angles for professional CMYK-style separation
    CMYK_SCREEN_ANGLES = [15, 75, 0, 45]  # Cyan, Magenta, Yellow, Black equivalents
    
    def __init__(self):
        """Initialize the image dithering node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for image dithering."""
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image to apply dithering effects"
                }),
                "method": (cls.DITHERING_METHODS, {
                    "default": cls.DEFAULT_METHOD,
                    "tooltip": "Dithering algorithm to apply"
                }),
                "color_mode": (cls.COLOR_MODES, {
                    "default": cls.DEFAULT_COLOR_MODE,
                    "tooltip": "Output as black & white or preserve color information"
                }),
                "threshold": ("FLOAT", {
                    "default": cls.DEFAULT_THRESHOLD,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Threshold value for pixel decisions (0.0 = black, 1.0 = white)"
                }),
                "dot_size": ("INT", {
                    "default": cls.DEFAULT_DOT_SIZE,
                    "min": 2,
                    "max": 16,
                    "step": 1,
                    "tooltip": "Dot size for halftone patterns (larger = coarser pattern)"
                }),
            },
            "optional": {
                "custom_angle": ("FLOAT", {
                    "default": 45.0,
                    "min": 0.0,
                    "max": 360.0,
                    "step": 1.0,
                    "tooltip": "Custom screen angle for halftone patterns (degrees)"
                }),
                "enhance_contrast": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Apply contrast enhancement before dithering"
                }),
            }
        }

    # Node metadata
    TITLE = "Image Dithering"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("dithered_image",)
    FUNCTION = "apply_dithering"
    CATEGORY = "unset"
    DESCRIPTION = "Apply professional dithering algorithms including Floyd-Steinberg, Bayer, and halftone patterns with color/monochrome support."

    def apply_dithering(self, image, method, color_mode, threshold, dot_size, custom_angle=45.0, enhance_contrast=False):
        """
        Apply selected dithering method to input image.
        
        Args:
            image: Input image tensor
            method: Dithering algorithm to use
            color_mode: Black & White or Color output
            threshold: Threshold for pixel decisions
            dot_size: Size for halftone dots
            custom_angle: Custom screen angle for halftone
            enhance_contrast: Whether to enhance contrast before dithering
            
        Returns:
            tuple: (dithered_image_tensor,)
        """
        try:
            # Process each image in the batch
            dithered_batch = []
            
            for i in range(image.shape[0]):
                single_image = image[i]
                dithered_image = self._process_single_image(
                    single_image, method, color_mode, threshold, 
                    dot_size, custom_angle, enhance_contrast
                )
                dithered_batch.append(dithered_image)
            
            # Concatenate batch results
            result_tensor = torch.cat(dithered_batch, dim=0)
            
            print(f"Applied {method} dithering in {color_mode} mode to {len(dithered_batch)} image(s)")
            
            return (result_tensor,)
            
        except Exception as e:
            error_msg = f"Dithering failed: {str(e)}"
            print(error_msg)
            # Return original image on error
            return (image,)

    def _process_single_image(self, image_tensor, method, color_mode, threshold, dot_size, custom_angle, enhance_contrast):
        """Process a single image with the specified dithering method."""
        # Convert tensor to numpy
        image_np = image_tensor.cpu().numpy()
        
        # Enhance contrast if requested
        if enhance_contrast:
            image_np = self._enhance_contrast(image_np)
        
        # Apply dithering based on color mode
        if color_mode == "Black & White":
            result_np = self._apply_monochrome_dithering(image_np, method, threshold, dot_size, custom_angle)
        else:  # Color mode
            result_np = self._apply_color_dithering(image_np, method, threshold, dot_size, custom_angle)
        
        # Convert back to tensor
        return torch.from_numpy(result_np).unsqueeze(0)

    def _enhance_contrast(self, image_np):
        """Apply contrast enhancement to image."""
        # Simple contrast stretch
        min_val = np.min(image_np)
        max_val = np.max(image_np)
        
        if max_val > min_val:
            enhanced = (image_np - min_val) / (max_val - min_val)
        else:
            enhanced = image_np
        
        return enhanced

    def _apply_monochrome_dithering(self, image_np, method, threshold, dot_size, custom_angle):
        """Apply dithering in black and white mode."""
        # Convert to grayscale if needed
        if len(image_np.shape) == 3:
            gray_image = self._rgb_to_grayscale(image_np)
        else:
            gray_image = image_np
        
        # Apply selected dithering method
        if method == "Floyd-Steinberg":
            result = self._floyd_steinberg_dither(gray_image, threshold)
        elif method == "Jarvis-Judice-Ninke":
            result = self._jarvis_judice_ninke_dither(gray_image, threshold)
        elif method == "Stucki":
            result = self._stucki_dither(gray_image, threshold)
        elif method == "Atkinson":
            result = self._atkinson_dither(gray_image, threshold)
        elif method == "Bayer 2x2":
            result = self._bayer_dither(gray_image, 2)
        elif method == "Bayer 4x4":
            result = self._bayer_dither(gray_image, 4)
        elif method == "Bayer 8x8":
            result = self._bayer_dither(gray_image, 8)
        elif method == "Halftone":
            result = self._halftone_dither(gray_image, dot_size, custom_angle)
        elif method == "Newspaper":
            result = self._halftone_dither(gray_image, 6, 45)  # Newspaper settings
        elif method == "Magazine":
            result = self._halftone_dither(gray_image, 3, 45)  # Magazine settings
        elif method == "Random":
            result = self._random_dither(gray_image, threshold)
        else:  # "None (Threshold)"
            result = self._threshold_dither(gray_image, threshold)
        
        # Convert to 3-channel for ComfyUI compatibility
        return np.stack([result, result, result], axis=-1)

    def _apply_color_dithering(self, image_np, method, threshold, dot_size, custom_angle):
        """Apply dithering in color mode."""
        # Ensure 3 channels
        if len(image_np.shape) == 2:
            image_np = np.stack([image_np, image_np, image_np], axis=-1)
        
        h, w, c = image_np.shape
        result = np.zeros_like(image_np)
        
        # Apply dithering to each channel
        for channel in range(c):
            channel_data = image_np[:, :, channel]
            
            if method == "Floyd-Steinberg":
                result[:, :, channel] = self._floyd_steinberg_dither(channel_data, threshold)
            elif method == "Jarvis-Judice-Ninke":
                result[:, :, channel] = self._jarvis_judice_ninke_dither(channel_data, threshold)
            elif method == "Stucki":
                result[:, :, channel] = self._stucki_dither(channel_data, threshold)
            elif method == "Atkinson":
                result[:, :, channel] = self._atkinson_dither(channel_data, threshold)
            elif method == "Bayer 2x2":
                result[:, :, channel] = self._bayer_dither(channel_data, 2)
            elif method == "Bayer 4x4":
                result[:, :, channel] = self._bayer_dither(channel_data, 4)
            elif method == "Bayer 8x8":
                result[:, :, channel] = self._bayer_dither(channel_data, 8)
            elif method == "Halftone":
                # Use different screen angles for professional color separation
                angle = self.CMYK_SCREEN_ANGLES[channel % len(self.CMYK_SCREEN_ANGLES)]
                result[:, :, channel] = self._halftone_dither(channel_data, dot_size, angle)
            elif method == "Newspaper":
                angle = self.CMYK_SCREEN_ANGLES[channel % len(self.CMYK_SCREEN_ANGLES)]
                result[:, :, channel] = self._halftone_dither(channel_data, 6, angle)
            elif method == "Magazine":
                angle = self.CMYK_SCREEN_ANGLES[channel % len(self.CMYK_SCREEN_ANGLES)]
                result[:, :, channel] = self._halftone_dither(channel_data, 3, angle)
            elif method == "Random":
                result[:, :, channel] = self._random_dither(channel_data, threshold)
            else:  # "None (Threshold)"
                result[:, :, channel] = self._threshold_dither(channel_data, threshold)
        
        return result

    def _rgb_to_grayscale(self, image_np):
        """Convert RGB image to grayscale using standard weights."""
        return (self.GRAYSCALE_WEIGHTS[0] * image_np[:, :, 0] + 
                self.GRAYSCALE_WEIGHTS[1] * image_np[:, :, 1] + 
                self.GRAYSCALE_WEIGHTS[2] * image_np[:, :, 2])

    # Dithering algorithm implementations
    def _floyd_steinberg_dither(self, image_array, threshold=0.5):
        """Floyd-Steinberg error diffusion dithering."""
        img = image_array.copy().astype(np.float32)
        h, w = img.shape
        
        for y in range(h):
            for x in range(w):
                old_pixel = img[y, x]
                new_pixel = 1.0 if old_pixel > threshold else 0.0
                img[y, x] = new_pixel
                error = old_pixel - new_pixel
                
                # Distribute error to neighboring pixels
                if x + 1 < w:
                    img[y, x + 1] += error * 7/16
                if y + 1 < h:
                    if x > 0:
                        img[y + 1, x - 1] += error * 3/16
                    img[y + 1, x] += error * 5/16
                    if x + 1 < w:
                        img[y + 1, x + 1] += error * 1/16
        
        return np.clip(img, 0, 1)

    def _jarvis_judice_ninke_dither(self, image_array, threshold=0.5):
        """Jarvis-Judice-Ninke error diffusion dithering."""
        img = image_array.copy().astype(np.float32)
        h, w = img.shape
        
        for y in range(h):
            for x in range(w):
                old_pixel = img[y, x]
                new_pixel = 1.0 if old_pixel > threshold else 0.0
                img[y, x] = new_pixel
                error = old_pixel - new_pixel
                
                # JJN error distribution pattern
                offsets = [
                    (0, 1, 7/48), (0, 2, 5/48),
                    (1, -2, 3/48), (1, -1, 5/48), (1, 0, 7/48), (1, 1, 5/48), (1, 2, 3/48),
                    (2, -2, 1/48), (2, -1, 3/48), (2, 0, 5/48), (2, 1, 3/48), (2, 2, 1/48)
                ]
                
                for dy, dx, weight in offsets:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        img[ny, nx] += error * weight
        
        return np.clip(img, 0, 1)

    def _stucki_dither(self, image_array, threshold=0.5):
        """Stucki error diffusion dithering."""
        img = image_array.copy().astype(np.float32)
        h, w = img.shape
        
        for y in range(h):
            for x in range(w):
                old_pixel = img[y, x]
                new_pixel = 1.0 if old_pixel > threshold else 0.0
                img[y, x] = new_pixel
                error = old_pixel - new_pixel
                
                # Stucki error distribution pattern
                offsets = [
                    (0, 1, 8/42), (0, 2, 4/42),
                    (1, -2, 2/42), (1, -1, 4/42), (1, 0, 8/42), (1, 1, 4/42), (1, 2, 2/42),
                    (2, -2, 1/42), (2, -1, 2/42), (2, 0, 4/42), (2, 1, 2/42), (2, 2, 1/42)
                ]
                
                for dy, dx, weight in offsets:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        img[ny, nx] += error * weight
        
        return np.clip(img, 0, 1)

    def _atkinson_dither(self, image_array, threshold=0.5):
        """Atkinson error diffusion dithering."""
        img = image_array.copy().astype(np.float32)
        h, w = img.shape
        
        for y in range(h):
            for x in range(w):
                old_pixel = img[y, x]
                new_pixel = 1.0 if old_pixel > threshold else 0.0
                img[y, x] = new_pixel
                error = old_pixel - new_pixel
                
                # Atkinson error distribution pattern
                offsets = [
                    (0, 1, 1/8), (0, 2, 1/8),
                    (1, -1, 1/8), (1, 0, 1/8), (1, 1, 1/8),
                    (2, 0, 1/8)
                ]
                
                for dy, dx, weight in offsets:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        img[ny, nx] += error * weight
        
        return np.clip(img, 0, 1)

    def _bayer_dither(self, image_array, matrix_size=2):
        """Bayer ordered dithering."""
        # Bayer matrices
        bayer_matrices = {
            2: np.array([[0, 2], [3, 1]]) / 4.0,
            4: np.array([
                [0, 8, 2, 10],
                [12, 4, 14, 6],
                [3, 11, 1, 9],
                [15, 7, 13, 5]
            ]) / 16.0,
            8: np.array([
                [0, 32, 8, 40, 2, 34, 10, 42],
                [48, 16, 56, 24, 50, 18, 58, 26],
                [12, 44, 4, 36, 14, 46, 6, 38],
                [60, 28, 52, 20, 62, 30, 54, 22],
                [3, 35, 11, 43, 1, 33, 9, 41],
                [51, 19, 59, 27, 49, 17, 57, 25],
                [15, 47, 7, 39, 13, 45, 5, 37],
                [63, 31, 55, 23, 61, 29, 53, 21]
            ]) / 64.0
        }
        
        bayer_matrix = bayer_matrices[matrix_size]
        h, w = image_array.shape
        result = np.zeros_like(image_array)
        
        for y in range(h):
            for x in range(w):
                threshold = bayer_matrix[y % matrix_size, x % matrix_size]
                result[y, x] = 1.0 if image_array[y, x] > threshold else 0.0
        
        return result

    def _halftone_dither(self, image_array, dot_size=4, angle=45):
        """Professional halftone dithering with rotation support."""
        h, w = image_array.shape
        result = np.ones_like(image_array)
        
        # Convert angle to radians
        angle_rad = np.radians(angle)
        cos_angle = np.cos(angle_rad)
        sin_angle = np.sin(angle_rad)
        
        for y in range(h):
            for x in range(w):
                # Apply rotation transformation
                transformed_x = x * cos_angle + y * sin_angle
                transformed_y = -x * sin_angle + y * cos_angle
                
                # Find halftone cell center
                cell_x = int(transformed_x // dot_size) * dot_size + dot_size // 2
                cell_y = int(transformed_y // dot_size) * dot_size + dot_size // 2
                
                # Transform back to image coordinates
                real_cell_x = cell_x * cos_angle - cell_y * sin_angle
                real_cell_y = cell_x * sin_angle + cell_y * cos_angle
                
                # Sample image brightness
                sample_x = int(np.clip(real_cell_x, 0, w - 1))
                sample_y = int(np.clip(real_cell_y, 0, h - 1))
                avg_brightness = image_array[sample_y, sample_x]
                
                # Calculate dot radius based on brightness
                dx = transformed_x - cell_x
                dy = transformed_y - cell_y
                distance_from_center = np.sqrt(dx * dx + dy * dy)
                
                max_radius = dot_size * 0.4
                dot_radius = max_radius * (1.0 - avg_brightness)
                
                result[y, x] = 0.0 if distance_from_center <= dot_radius else 1.0
        
        return result

    def _random_dither(self, image_array, threshold=0.5):
        """Random threshold dithering."""
        h, w = image_array.shape
        random_thresholds = np.random.random((h, w)) * 0.5 + (threshold - 0.25)
        return (image_array > random_thresholds).astype(np.float32)

    def _threshold_dither(self, image_array, threshold=0.5):
        """Simple threshold (no dithering)."""
        return (image_array > threshold).astype(np.float32)


