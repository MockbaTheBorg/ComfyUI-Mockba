"""
Image Film Effect Node for ComfyUI
Adds realistic film grain, vignette, and other film-like effects to images.
"""

# Standard library imports
import torch
import numpy as np
import math
from PIL import Image, ImageEnhance

# Use numeric value for LANCZOS to avoid version compatibility issues
LANCZOS = 1  # PIL.Image.LANCZOS constant value

class mbImageFilmEffect:
    """Add realistic film grain, vignette, and film-like effects to images."""
    
    # Class constants
    FILM_TYPES = ["black_and_white", "color_negative", "slide_film", "instant_film", "vintage_color"]
    DEFAULT_FILM_TYPE = "color_negative"
    
    def __init__(self):
        """Initialize the film effect node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for film effects."""
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image tensor to apply film effects"
                }),
                "film_type": (cls.FILM_TYPES, {
                    "default": cls.DEFAULT_FILM_TYPE,
                    "tooltip": "Type of film to simulate"
                }),
                "grain_strength": ("INT", {
                    "default": 40,
                    "min": 0,
                    "max": 100,
                    "tooltip": "Film grain intensity (0 = no grain, 100 = heavy grain)"
                }),
                "vignette_strength": ("INT", {
                    "default": 35,
                    "min": 0,
                    "max": 100,
                    "tooltip": "Vignette darkness around edges (0 = none, 100 = heavy)"
                }),
                "contrast_boost": ("INT", {
                    "default": 20,
                    "min": 0,
                    "max": 50,
                    "tooltip": "Film-like contrast enhancement"
                }),
                "color_shift": ("INT", {
                    "default": 50,
                    "min": 0,
                    "max": 50,
                    "tooltip": "Color temperature/tint shift typical of film"
                }),
                "dust_spots": ("INT", {
                    "default": 15,
                    "min": 0,
                    "max": 50,
                    "tooltip": "Add subtle dust spots and imperfections"
                }),
                "dead_pixels": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 30,
                    "tooltip": "Add dead/stuck pixels (0 = none, 30 = many)"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999,
                    "tooltip": "Seed for dust spots and dead pixel positioning"
                }),
            }
        }

    # Node metadata
    TITLE = "Image Film Effect"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "apply_film_effects"
    CATEGORY = "unset"
    DESCRIPTION = "Add realistic film grain, vignette, and other film-like effects to make images look like analog photography."

    def apply_film_effects(self, image, film_type, grain_strength, vignette_strength, contrast_boost, color_shift, dust_spots, dead_pixels, seed):
        """
        Apply film effects to the input image.
        
        Args:
            image: Input image tensor in ComfyUI format [batch, height, width, channels]
            film_type: Type of film to simulate
            grain_strength: Film grain intensity (0-100)
            vignette_strength: Vignette intensity (0-100)
            contrast_boost: Contrast enhancement (0-50)
            color_shift: Color temperature shift (0-50)
            dust_spots: Number of dust spots/imperfections (0-50)
            dead_pixels: Number of dead/stuck pixels (0-30)
            seed: Seed for dust spots and dead pixel positioning
            
        Returns:
            tuple: Image with film effects applied
        """
        try:
            # Validate input tensor
            if torch.any(torch.isnan(image)) or torch.any(torch.isinf(image)):
                print("Warning: Input image contains NaN or infinite values, cleaning...")
                image = torch.nan_to_num(image, nan=0.0, posinf=1.0, neginf=0.0)
            
            # Ensure image values are in valid range [0, 1]
            image = torch.clamp(image, 0.0, 1.0)
            
            # Process each image in the batch
            processed_images = []
            
            for i in range(image.shape[0]):
                # Convert to PIL for processing
                img_np = (image[i].cpu().numpy() * 255).astype(np.uint8)
                pil_img = Image.fromarray(img_np)
                
                # Apply film effects in order
                if grain_strength > 0:
                    pil_img = self._add_film_grain(pil_img, grain_strength, film_type)
                
                if vignette_strength > 0:
                    pil_img = self._add_vignette(pil_img, vignette_strength)
                
                if contrast_boost > 0:
                    pil_img = self._enhance_contrast(pil_img, contrast_boost, film_type)
                
                if color_shift > 0:
                    pil_img = self._apply_color_shift(pil_img, color_shift, film_type)
                
                if dust_spots > 0:
                    pil_img = self._add_dust_spots(pil_img, dust_spots, seed)
                
                if dead_pixels > 0:
                    pil_img = self._add_dead_pixels(pil_img, dead_pixels, seed)
                
                # Convert back to tensor
                img_np = np.array(pil_img).astype(np.float32) / 255.0
                
                # Validate the result
                if np.any(np.isnan(img_np)) or np.any(np.isinf(img_np)):
                    print("Warning: NaN or infinite values detected in result, using original image")
                    img_np = image[i].cpu().numpy()
                
                img_tensor = torch.from_numpy(img_np).to(image.device)
                processed_images.append(img_tensor)
            
            # Stack all processed images
            result = torch.stack(processed_images, dim=0)
            
            return (result,)
            
        except Exception as e:
            error_msg = f"Failed to apply film effects: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)

    def _add_film_grain(self, img, strength, film_type):
        """Add realistic film grain based on film type."""
        if strength <= 0:
            return img
        
        img_array = np.array(img).astype(np.float32)
        h, w = img_array.shape[:2]
        
        # Create grain pattern based on film type
        if film_type == "black_and_white":
            # Fine, uniform grain
            grain_size = max(1, min(h, w) // 600)
            grain_strength = (strength / 100.0) * 12.0
        elif film_type == "color_negative":
            # Medium grain with slight color variation
            grain_size = max(1, min(h, w) // 500)
            grain_strength = (strength / 100.0) * 10.0
        elif film_type == "slide_film":
            # Very fine grain, high quality
            grain_size = max(1, min(h, w) // 800)
            grain_strength = (strength / 100.0) * 6.0
        elif film_type == "instant_film":
            # Coarse, visible grain
            grain_size = max(1, min(h, w) // 300)
            grain_strength = (strength / 100.0) * 15.0
        else:  # vintage_color
            # Heavy, irregular grain
            grain_size = max(1, min(h, w) // 400)
            grain_strength = (strength / 100.0) * 18.0
        
        # Generate deterministic grain pattern
        yy, xx = np.mgrid[0:h:grain_size, 0:w:grain_size]
        grain_pattern = np.sin(xx * 0.97) * np.cos(yy * 0.73) + np.sin(xx * 1.23) * np.cos(yy * 1.47)
        grain_pattern = (grain_pattern + 1) / 2  # Normalize to [0, 1]
        
        # Resize grain to image dimensions
        from PIL import Image as PILImage
        grain_img = PILImage.fromarray((grain_pattern * 255).astype(np.uint8), mode='L')
        grain_img = grain_img.resize((w, h), LANCZOS)
        grain_array = np.array(grain_img).astype(np.float32) / 255.0
        
        # Apply grain to image
        grain_effect = (grain_array - 0.5) * grain_strength
        img_array += grain_effect[:, :, np.newaxis]
        
        # Add color grain for color films
        if film_type in ["color_negative", "vintage_color", "instant_film"]:
            color_grain_strength = grain_strength * 0.3
            for c in range(min(3, img_array.shape[2])):
                channel_grain = np.sin(xx * (1.1 + c * 0.2)) * np.cos(yy * (0.8 + c * 0.15))
                channel_grain = PILImage.fromarray(((channel_grain + 1) * 127.5).astype(np.uint8), mode='L')
                channel_grain = channel_grain.resize((w, h), LANCZOS)
                channel_grain = np.array(channel_grain).astype(np.float32) / 255.0
                img_array[:, :, c] += (channel_grain - 0.5) * color_grain_strength
        
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        return Image.fromarray(img_array)

    def _add_vignette(self, img, strength):
        """Add realistic vignette effect."""
        if strength <= 0:
            return img
        
        img_array = np.array(img).astype(np.float32)
        h, w = img_array.shape[:2]
        
        # Create vignette mask
        center_x, center_y = w / 2, h / 2
        max_dist = math.sqrt(center_x**2 + center_y**2)
        
        y, x = np.ogrid[:h, :w]
        distances = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Create smooth vignette
        vignette_strength = (strength / 100.0) * 0.6  # Max 60% darkening
        vignette = 1 - (distances / max_dist) * vignette_strength
        
        # Apply smooth falloff
        vignette = np.power(vignette, 1.5)  # Non-linear falloff
        vignette = np.clip(vignette, 0.4, 1.0)  # Don't go completely black
        
        img_array *= vignette[:, :, np.newaxis]
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        
        return Image.fromarray(img_array)

    def _enhance_contrast(self, img, boost, film_type):
        """Apply film-specific contrast enhancement."""
        if boost <= 0:
            return img
        
        # Different contrast curves for different film types
        if film_type == "black_and_white":
            # High contrast, deep blacks
            contrast_factor = 1.0 + (boost / 100.0) * 0.8
        elif film_type == "slide_film":
            # Very high contrast and saturation
            contrast_factor = 1.0 + (boost / 100.0) * 1.2
        elif film_type == "instant_film":
            # Softer contrast, lifted blacks
            contrast_factor = 1.0 + (boost / 100.0) * 0.4
        else:  # color_negative, vintage_color
            # Moderate contrast enhancement
            contrast_factor = 1.0 + (boost / 100.0) * 0.6
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast_factor)
        
        # Add slight S-curve for film look
        if film_type in ["slide_film", "black_and_white"]:
            img_array = np.array(img).astype(np.float32) / 255.0
            # Simple S-curve
            img_array = np.power(img_array, 0.9) * 1.1
            img_array = np.clip(img_array * 255, 0, 255).astype(np.uint8)
            img = Image.fromarray(img_array)
        
        return img

    def _apply_color_shift(self, img, shift_strength, film_type):
        """Apply color shifts typical of different film types."""
        if shift_strength <= 0:
            return img
        
        img_array = np.array(img).astype(np.float32)
        shift_factor = shift_strength / 100.0
        
        if film_type == "color_negative":
            # Slight warm shift, orange/yellow cast
            img_array[:, :, 0] *= (1 + shift_factor * 0.15)  # More red
            img_array[:, :, 1] *= (1 + shift_factor * 0.08)  # Slight yellow
            img_array[:, :, 2] *= (1 - shift_factor * 0.05)  # Less blue
        
        elif film_type == "slide_film":
            # Saturated, slightly cool
            enhancer = ImageEnhance.Color(Image.fromarray(img_array.astype(np.uint8)))
            img = enhancer.enhance(1 + shift_factor * 0.3)
            img_array = np.array(img).astype(np.float32)
            img_array[:, :, 2] *= (1 + shift_factor * 0.1)  # More blue
        
        elif film_type == "instant_film":
            # Green/magenta shift typical of Polaroid
            img_array[:, :, 1] *= (1 + shift_factor * 0.12)  # Green cast
            img_array[:, :, 0] *= (1 - shift_factor * 0.05)  # Less red
        
        elif film_type == "vintage_color":
            # Faded, desaturated with yellow aging
            enhancer = ImageEnhance.Color(Image.fromarray(img_array.astype(np.uint8)))
            img = enhancer.enhance(1 - shift_factor * 0.2)  # Desaturate
            img_array = np.array(img).astype(np.float32)
            img_array[:, :, 0] *= (1 + shift_factor * 0.2)  # Yellow/red aging
            img_array[:, :, 1] *= (1 + shift_factor * 0.15)
        
        # Black and white films don't get color shifts
        
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        return Image.fromarray(img_array)

    def _add_dust_spots(self, img, spot_count, seed):
        """Add subtle dust spots and imperfections."""
        if spot_count <= 0:
            return img
        
        img_array = np.array(img).astype(np.float32)
        h, w = img_array.shape[:2]
        
        # Generate deterministic dust spots based on seed and image dimensions
        np.random.seed((seed + hash((h, w))) % (2**32))
        
        num_spots = int(spot_count / 2)  # Reduce actual number
        
        for i in range(num_spots):
            # Random position
            x = np.random.randint(0, w)
            y = np.random.randint(0, h)
            
            # Small dust spot (1-3 pixels radius)
            radius = np.random.randint(1, 4)
            
            # Dust opacity
            opacity = np.random.uniform(0.1, 0.4)
            
            # Create circular dust spot
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    px, py = x + dx, y + dy
                    if (0 <= px < w and 0 <= py < h and 
                        dx*dx + dy*dy <= radius*radius):
                        
                        # Darker spot (dust reduces light)
                        img_array[py, px] *= (1 - opacity)
        
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        return Image.fromarray(img_array)

    def _add_dead_pixels(self, img, dead_pixel_count, seed):
        """Add dead/stuck pixel simulation."""
        if dead_pixel_count <= 0:
            return img
        
        img_array = np.array(img).astype(np.float32)
        h, w = img_array.shape[:2]
        
        # Generate deterministic dead pixels based on seed and image dimensions
        # Use a different seed offset to ensure dead pixels don't overlap with dust spots
        np.random.seed((seed * 2 + 1000 + hash((h, w))) % (2**32))
        
        for i in range(dead_pixel_count):
            # Random position for dead pixel
            x = np.random.randint(0, w)
            y = np.random.randint(0, h)
            
            # Type of dead pixel
            pixel_type = np.random.choice(['dead', 'stuck_red', 'stuck_green', 'stuck_blue', 'stuck_white'])
            
            if pixel_type == 'dead':
                # Dead pixel - completely black
                img_array[y, x] = [0, 0, 0]
            elif pixel_type == 'stuck_red':
                # Stuck red pixel
                img_array[y, x] = [255, 0, 0]
            elif pixel_type == 'stuck_green':
                # Stuck green pixel
                img_array[y, x] = [0, 255, 0]
            elif pixel_type == 'stuck_blue':
                # Stuck blue pixel
                img_array[y, x] = [0, 0, 255]
            elif pixel_type == 'stuck_white':
                # Stuck white pixel - always on
                img_array[y, x] = [255, 255, 255]
            
            # Occasionally create small clusters (2-4 adjacent dead pixels)
            if np.random.random() < 0.3:  # 30% chance for clusters
                cluster_size = np.random.randint(1, 4)
                for _ in range(cluster_size):
                    # Adjacent pixel within 2 pixels
                    offset_x = np.random.randint(-2, 3)
                    offset_y = np.random.randint(-2, 3)
                    cluster_x = np.clip(x + offset_x, 0, w - 1)
                    cluster_y = np.clip(y + offset_y, 0, h - 1)
                    
                    # Same type of dead pixel for the cluster
                    if pixel_type == 'dead':
                        img_array[cluster_y, cluster_x] = [0, 0, 0]
                    elif pixel_type == 'stuck_red':
                        img_array[cluster_y, cluster_x] = [255, 0, 0]
                    elif pixel_type == 'stuck_green':
                        img_array[cluster_y, cluster_x] = [0, 255, 0]
                    elif pixel_type == 'stuck_blue':
                        img_array[cluster_y, cluster_x] = [0, 0, 255]
                    elif pixel_type == 'stuck_white':
                        img_array[cluster_y, cluster_x] = [255, 255, 255]
        
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        return Image.fromarray(img_array)
