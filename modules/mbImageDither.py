import torch
import numpy as np
from PIL import Image

# Converts an image to black and white using various dithering methods
class mbImageDither:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": ("IMAGE",),
                "method": (["Floyd-Steinberg", "Jarvis-Judice-Ninke", "Stucki", "Atkinson", "Bayer 2x2", "Bayer 4x4", "Bayer 8x8", "Halftone", "Newspaper", "Magazine", "Random", "None (Threshold)"], {"default": "Floyd-Steinberg"}),
                "color_mode": (["Black & White", "Color"], {"default": "Black & White"}),
                "threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "dot_size": ("INT", {"default": 4, "min": 2, "max": 16, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "dither"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Converts an image to black and white or applies color dithering using various methods."

    def floyd_steinberg_dither(self, image_array, threshold=0.5):
        """Floyd-Steinberg error diffusion dithering"""
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

    def jarvis_judice_ninke_dither(self, image_array, threshold=0.5):
        """Jarvis-Judice-Ninke error diffusion dithering"""
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

    def stucki_dither(self, image_array, threshold=0.5):
        """Stucki error diffusion dithering"""
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

    def atkinson_dither(self, image_array, threshold=0.5):
        """Atkinson error diffusion dithering"""
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

    def bayer_dither(self, image_array, matrix_size=2):
        """Bayer ordered dithering"""
        # Bayer matrices
        bayer_2x2 = np.array([[0, 2], [3, 1]]) / 4.0
        bayer_4x4 = np.array([
            [0, 8, 2, 10],
            [12, 4, 14, 6],
            [3, 11, 1, 9],
            [15, 7, 13, 5]
        ]) / 16.0
        bayer_8x8 = np.array([
            [0, 32, 8, 40, 2, 34, 10, 42],
            [48, 16, 56, 24, 50, 18, 58, 26],
            [12, 44, 4, 36, 14, 46, 6, 38],
            [60, 28, 52, 20, 62, 30, 54, 22],
            [3, 35, 11, 43, 1, 33, 9, 41],
            [51, 19, 59, 27, 49, 17, 57, 25],
            [15, 47, 7, 39, 13, 45, 5, 37],
            [63, 31, 55, 23, 61, 29, 53, 21]
        ]) / 64.0
        
        matrix_map = {2: bayer_2x2, 4: bayer_4x4, 8: bayer_8x8}
        bayer_matrix = matrix_map[matrix_size]
        
        h, w = image_array.shape
        result = np.zeros_like(image_array)
        
        for y in range(h):
            for x in range(w):
                threshold = bayer_matrix[y % matrix_size, x % matrix_size]
                result[y, x] = 1.0 if image_array[y, x] > threshold else 0.0
        
        return result

    def random_dither(self, image_array, threshold=0.5):
        """Random threshold dithering"""
        h, w = image_array.shape
        random_thresholds = np.random.random((h, w)) * 0.5 + (threshold - 0.25)
        return (image_array > random_thresholds).astype(np.float32)

    def threshold_dither(self, image_array, threshold=0.5):
        """Simple threshold (no dithering)"""
        return (image_array > threshold).astype(np.float32)

    def halftone_dither(self, image_array, dot_size=4, angle=45, offset_x=0, offset_y=0):
        """Halftone dithering - simulates print media dot patterns with angle and offset control"""
        h, w = image_array.shape
        result = np.ones_like(image_array)  # Start with white background
        
        # Convert angle to radians
        angle_rad = np.radians(angle)
        cos_angle = np.cos(angle_rad)
        sin_angle = np.sin(angle_rad)
        
        # Create rotated grid by transforming coordinates
        for y in range(h):
            for x in range(w):
                # Apply inverse rotation to find which halftone cell this pixel belongs to
                # Add offset to shift the entire grid
                transformed_x = (x + offset_x) * cos_angle + (y + offset_y) * sin_angle
                transformed_y = -(x + offset_x) * sin_angle + (y + offset_y) * cos_angle
                
                # Find the halftone cell center
                cell_x = int(transformed_x // dot_size) * dot_size + dot_size // 2
                cell_y = int(transformed_y // dot_size) * dot_size + dot_size // 2
                
                # Transform cell center back to image coordinates
                real_cell_x = cell_x * cos_angle - cell_y * sin_angle
                real_cell_y = cell_x * sin_angle + cell_y * cos_angle
                
                # Sample the image brightness around this cell center
                sample_x = int(np.clip(real_cell_x - offset_x, 0, w - 1))
                sample_y = int(np.clip(real_cell_y - offset_y, 0, h - 1))
                
                # Get average brightness in a small area around the sample point
                sample_size = max(1, dot_size // 3)
                x_start = max(0, sample_x - sample_size)
                x_end = min(w, sample_x + sample_size + 1)
                y_start = max(0, sample_y - sample_size)
                y_end = min(h, sample_y + sample_size + 1)
                
                if x_start < x_end and y_start < y_end:
                    avg_brightness = np.mean(image_array[y_start:y_end, x_start:x_end])
                else:
                    avg_brightness = image_array[sample_y, sample_x]
                
                # Calculate distance from current pixel to cell center
                dx = transformed_x - cell_x
                dy = transformed_y - cell_y
                distance_from_center = np.sqrt(dx * dx + dy * dy)
                
                # Calculate dot radius based on brightness (darker = larger dots)
                max_radius = dot_size * 0.4  # Slightly smaller than half to prevent overlap
                dot_radius = max_radius * (1.0 - avg_brightness)
                
                # Set pixel based on whether it's inside the dot
                if distance_from_center <= dot_radius:
                    result[y, x] = 0.0  # Black dot
                else:
                    result[y, x] = 1.0  # White background
        
        return result

    def newspaper_dither(self, image_array, dot_size=6):
        """Newspaper-style halftone (lower quality, larger dots)"""
        return self.halftone_dither(image_array, dot_size, angle=45, offset_x=0, offset_y=0)

    def magazine_dither(self, image_array, dot_size=3):
        """Magazine-style halftone (higher quality, smaller dots)"""
        return self.halftone_dither(image_array, dot_size, angle=45, offset_x=0, offset_y=0)

    # Color dithering methods - apply dithering per channel
    def floyd_steinberg_color_dither(self, image_array, threshold=0.5):
        """Floyd-Steinberg error diffusion for color images"""
        if len(image_array.shape) == 2:
            return self.floyd_steinberg_dither(image_array, threshold)
        
        h, w, c = image_array.shape
        result = np.zeros_like(image_array)
        
        for channel in range(c):
            result[:, :, channel] = self.floyd_steinberg_dither(image_array[:, :, channel], threshold)
        
        return result

    def jarvis_judice_ninke_color_dither(self, image_array, threshold=0.5):
        """JJN error diffusion for color images"""
        if len(image_array.shape) == 2:
            return self.jarvis_judice_ninke_dither(image_array, threshold)
        
        h, w, c = image_array.shape
        result = np.zeros_like(image_array)
        
        for channel in range(c):
            result[:, :, channel] = self.jarvis_judice_ninke_dither(image_array[:, :, channel], threshold)
        
        return result

    def stucki_color_dither(self, image_array, threshold=0.5):
        """Stucki error diffusion for color images"""
        if len(image_array.shape) == 2:
            return self.stucki_dither(image_array, threshold)
        
        h, w, c = image_array.shape
        result = np.zeros_like(image_array)
        
        for channel in range(c):
            result[:, :, channel] = self.stucki_dither(image_array[:, :, channel], threshold)
        
        return result

    def atkinson_color_dither(self, image_array, threshold=0.5):
        """Atkinson error diffusion for color images"""
        if len(image_array.shape) == 2:
            return self.atkinson_dither(image_array, threshold)
        
        h, w, c = image_array.shape
        result = np.zeros_like(image_array)
        
        for channel in range(c):
            result[:, :, channel] = self.atkinson_dither(image_array[:, :, channel], threshold)
        
        return result

    def bayer_color_dither(self, image_array, matrix_size=2):
        """Bayer ordered dithering for color images"""
        if len(image_array.shape) == 2:
            return self.bayer_dither(image_array, matrix_size)
        
        h, w, c = image_array.shape
        result = np.zeros_like(image_array)
        
        for channel in range(c):
            result[:, :, channel] = self.bayer_dither(image_array[:, :, channel], matrix_size)
        
        return result

    def random_color_dither(self, image_array, threshold=0.5):
        """Random threshold dithering for color images"""
        if len(image_array.shape) == 2:
            return self.random_dither(image_array, threshold)
        
        h, w, c = image_array.shape
        result = np.zeros_like(image_array)
        
        for channel in range(c):
            result[:, :, channel] = self.random_dither(image_array[:, :, channel], threshold)
        
        return result

    def threshold_color_dither(self, image_array, threshold=0.5):
        """Simple threshold for color images"""
        if len(image_array.shape) == 2:
            return self.threshold_dither(image_array, threshold)
        
        h, w, c = image_array.shape
        result = np.zeros_like(image_array)
        
        for channel in range(c):
            result[:, :, channel] = self.threshold_dither(image_array[:, :, channel], threshold)
        
        return result

    def halftone_color_dither(self, image_array, dot_size=4, angle=45):
        """Halftone dithering for color images with professional CMYK-style screen angles"""
        if len(image_array.shape) == 2:
            return self.halftone_dither(image_array, dot_size, angle)
        
        h, w, c = image_array.shape
        result = np.zeros_like(image_array)
        
        # Professional CMYK screen angles and offsets to prevent moiré patterns
        # These are industry-standard angles used in commercial printing
        screen_settings = [
            {"angle": 15, "offset_x": 0, "offset_y": 0},      # Cyan equivalent (Red channel)
            {"angle": 75, "offset_x": dot_size//3, "offset_y": 0},  # Magenta equivalent (Green channel)  
            {"angle": 0, "offset_x": dot_size//2, "offset_y": dot_size//3},   # Yellow equivalent (Blue channel)
        ]
        
        # If we have more than 3 channels, use additional angles
        if c > 3:
            screen_settings.append({"angle": 45, "offset_x": dot_size//4, "offset_y": dot_size//2})
        
        for channel in range(c):
            settings = screen_settings[channel % len(screen_settings)]
            result[:, :, channel] = self.halftone_dither(
                image_array[:, :, channel], 
                dot_size, 
                settings["angle"],
                settings["offset_x"],
                settings["offset_y"]
            )
        
        return result

    def dither(self, image, method, color_mode, threshold, dot_size):
        def convert_to_dithered_tensor(image_tensor, method, color_mode, threshold, dot_size):
            image_np = image_tensor.cpu().numpy().squeeze()
            
            if color_mode == "Black & White":
                # Convert to grayscale first
                if len(image_np.shape) == 3:
                    # Convert RGB to grayscale
                    image_gray = 0.299 * image_np[:, :, 0] + 0.587 * image_np[:, :, 1] + 0.114 * image_np[:, :, 2]
                else:
                    image_gray = image_np
                
                # Apply selected dithering method
                if method == "Floyd-Steinberg":
                    result = self.floyd_steinberg_dither(image_gray, threshold)
                elif method == "Jarvis-Judice-Ninke":
                    result = self.jarvis_judice_ninke_dither(image_gray, threshold)
                elif method == "Stucki":
                    result = self.stucki_dither(image_gray, threshold)
                elif method == "Atkinson":
                    result = self.atkinson_dither(image_gray, threshold)
                elif method == "Bayer 2x2":
                    result = self.bayer_dither(image_gray, 2)
                elif method == "Bayer 4x4":
                    result = self.bayer_dither(image_gray, 4)
                elif method == "Bayer 8x8":
                    result = self.bayer_dither(image_gray, 8)
                elif method == "Halftone":
                    result = self.halftone_dither(image_gray, dot_size, angle=45, offset_x=0, offset_y=0)
                elif method == "Newspaper":
                    result = self.newspaper_dither(image_gray)
                elif method == "Magazine":
                    result = self.magazine_dither(image_gray)
                elif method == "Random":
                    result = self.random_dither(image_gray, threshold)
                else:  # "None (Threshold)"
                    result = self.threshold_dither(image_gray, threshold)
                
                # Convert back to 3-channel for ComfyUI compatibility
                result_3d = np.stack([result, result, result], axis=-1)
                
            else:  # Color mode
                # Ensure we have 3 channels
                if len(image_np.shape) == 2:
                    image_np = np.stack([image_np, image_np, image_np], axis=-1)
                
                # Apply color dithering method
                if method == "Floyd-Steinberg":
                    result_3d = self.floyd_steinberg_color_dither(image_np, threshold)
                elif method == "Jarvis-Judice-Ninke":
                    result_3d = self.jarvis_judice_ninke_color_dither(image_np, threshold)
                elif method == "Stucki":
                    result_3d = self.stucki_color_dither(image_np, threshold)
                elif method == "Atkinson":
                    result_3d = self.atkinson_color_dither(image_np, threshold)
                elif method == "Bayer 2x2":
                    result_3d = self.bayer_color_dither(image_np, 2)
                elif method == "Bayer 4x4":
                    result_3d = self.bayer_color_dither(image_np, 4)
                elif method == "Bayer 8x8":
                    result_3d = self.bayer_color_dither(image_np, 8)
                elif method == "Halftone":
                    result_3d = self.halftone_color_dither(image_np, dot_size)
                elif method == "Newspaper":
                    result_3d = self.halftone_color_dither(image_np, 6)  # Newspaper dot size
                elif method == "Magazine":
                    result_3d = self.halftone_color_dither(image_np, 3)  # Magazine dot size
                elif method == "Random":
                    result_3d = self.random_color_dither(image_np, threshold)
                else:  # "None (Threshold)"
                    result_3d = self.threshold_color_dither(image_np, threshold)
            
            return torch.from_numpy(result_3d).unsqueeze(0)

        dithered_tensor = torch.empty(0)
        for i in range(image.shape[0]):
            dithered_tensor = torch.cat((dithered_tensor, convert_to_dithered_tensor(image[i], method, color_mode, threshold, dot_size)), dim=0)
    
        return (dithered_tensor,)

