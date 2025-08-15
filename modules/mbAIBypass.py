"""
AI Detection Bypass Node for ComfyUI
Modifies images to help them pass FFT-based AI detection by adding natural artifacts and noise patterns.
"""

# Standard library imports
import torch
import numpy as np
import math
from PIL import Image, ImageFilter, ImageEnhance

# Local imports
from .common import CATEGORIES


class mbAIBypass:
    """Add natural artifacts and noise patterns to help images pass AI detection systems."""
    
    # Class constants
    BYPASS_MODES = ["subtle", "moderate", "aggressive", "custom"]
    NOISE_TYPES = ["sensor", "film_grain", "gaussian", "perlin", "mixed"]
    DEFAULT_MODE = "moderate"
    DEFAULT_NOISE = "mixed"
    
    def __init__(self):
        """Initialize the AI bypass node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for AI bypass processing."""
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image tensor to process for AI detection bypass"
                }),
                "bypass_mode": (cls.BYPASS_MODES, {
                    "default": cls.DEFAULT_MODE,
                    "tooltip": "Intensity level of bypass modifications"
                }),
                "noise_type": (cls.NOISE_TYPES, {
                    "default": cls.DEFAULT_NOISE,
                    "tooltip": "Type of noise pattern to add"
                }),
                "high_freq_boost": ("FLOAT", {
                    "default": 0.3,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Boost high frequency components (0 = none, 1 = maximum)"
                }),
                "texture_enhancement": ("FLOAT", {
                    "default": 0.25,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Add micro-textures to smooth regions"
                }),
                "edge_imperfection": ("FLOAT", {
                    "default": 0.2,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Add subtle imperfections to edges"
                }),
                "compression_artifacts": ("FLOAT", {
                    "default": 0.15,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Simulate realistic compression artifacts"
                }),
            },
            "optional": {
                "preserve_quality": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Prioritize visual quality while applying modifications"
                }),
                "adaptive_processing": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Adapt processing strength based on image content"
                }),
                "seed": ("INT", {
                    "default": 42,
                    "min": 0,
                    "max": 999999999,
                    "tooltip": "Random seed for reproducible results"
                })
            }
        }

    # Node metadata
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "processing_info")
    FUNCTION = "apply_ai_bypass"
    CATEGORY = CATEGORIES["IMAGE_PROCESSING"]
    DESCRIPTION = "Modify images to help pass AI detection by adding natural artifacts, noise patterns, and frequency domain modifications."

    def apply_ai_bypass(self, image, bypass_mode, noise_type, high_freq_boost, texture_enhancement, 
                       edge_imperfection, compression_artifacts, preserve_quality=True, 
                       adaptive_processing=True, seed=42):
        """
        Apply AI detection bypass modifications to an image.
        
        Args:
            image: Input image tensor
            bypass_mode: Intensity level of modifications
            noise_type: Type of noise to add
            high_freq_boost: High frequency enhancement strength
            texture_enhancement: Micro-texture addition strength
            edge_imperfection: Edge imperfection strength
            compression_artifacts: Compression artifact simulation strength
            preserve_quality: Whether to prioritize visual quality
            adaptive_processing: Whether to adapt based on content
            seed: Random seed for reproducible results
            
        Returns:
            tuple: (modified_image, processing_info)
        """
        try:
            # Set random seed for reproducibility
            np.random.seed(seed)
            torch.manual_seed(seed)
            
            # Convert tensor to numpy for processing
            img_array = self._tensor_to_numpy(image)
            height, width = img_array.shape[:2]
            
            # Apply mode-specific parameter adjustments
            params = self._get_mode_parameters(bypass_mode, high_freq_boost, texture_enhancement, 
                                             edge_imperfection, compression_artifacts)
            
            # Initialize processing info
            info_parts = [f"Mode: {bypass_mode}", f"Noise: {noise_type}"]
            
            # Apply various bypass techniques
            processed_img = img_array.copy()
            
            # 1. High frequency enhancement via FFT
            if params['high_freq_boost'] > 0:
                processed_img = self._enhance_high_frequencies(processed_img, params['high_freq_boost'])
                info_parts.append(f"High freq boost: {params['high_freq_boost']:.2f}")
            
            # 2. Add realistic noise patterns
            if params['noise_strength'] > 0:
                processed_img = self._add_realistic_noise(processed_img, noise_type, params['noise_strength'], adaptive_processing)
                info_parts.append(f"Noise added: {noise_type}")
            
            # 3. Enhance textures in smooth regions
            if params['texture_enhancement'] > 0:
                processed_img = self._enhance_textures(processed_img, params['texture_enhancement'], adaptive_processing)
                info_parts.append(f"Texture enhancement: {params['texture_enhancement']:.2f}")
            
            # 4. Add edge imperfections
            if params['edge_imperfection'] > 0:
                processed_img = self._add_edge_imperfections(processed_img, params['edge_imperfection'])
                info_parts.append(f"Edge imperfections: {params['edge_imperfection']:.2f}")
            
            # 5. Simulate compression artifacts
            if params['compression_artifacts'] > 0:
                processed_img = self._simulate_compression_artifacts(processed_img, params['compression_artifacts'])
                info_parts.append(f"Compression artifacts: {params['compression_artifacts']:.2f}")
            
            # 6. Add subtle chromatic aberration
            if params['chromatic_aberration'] > 0:
                processed_img = self._add_chromatic_aberration(processed_img, params['chromatic_aberration'])
                info_parts.append("Chromatic aberration added")
            
            # 7. Apply quality preservation if enabled
            if preserve_quality:
                processed_img = self._preserve_quality(img_array, processed_img, 0.95)
                info_parts.append("Quality preserved")
            
            # Ensure values are in valid range
            processed_img = np.clip(processed_img, 0.0, 1.0)
            
            # Convert back to tensor
            result_tensor = self._numpy_to_tensor(processed_img)
            
            processing_info = " | ".join(info_parts)
            
            return (result_tensor, processing_info)
            
        except Exception as e:
            # Return original image on error
            error_info = f"Error during AI bypass processing: {str(e)}"
            return (image, error_info)

    def _get_mode_parameters(self, mode, high_freq_boost, texture_enhancement, edge_imperfection, compression_artifacts):
        """Get processing parameters based on bypass mode."""
        base_params = {
            'high_freq_boost': high_freq_boost,
            'texture_enhancement': texture_enhancement,
            'edge_imperfection': edge_imperfection,
            'compression_artifacts': compression_artifacts,
            'noise_strength': 0.0,
            'chromatic_aberration': 0.0
        }
        
        if mode == "subtle":
            multiplier = 0.5
            base_params['noise_strength'] = 0.02
            base_params['chromatic_aberration'] = 0.01
        elif mode == "moderate":
            multiplier = 1.0
            base_params['noise_strength'] = 0.04
            base_params['chromatic_aberration'] = 0.02
        elif mode == "aggressive":
            multiplier = 1.5
            base_params['noise_strength'] = 0.06
            base_params['chromatic_aberration'] = 0.03
        else:  # custom
            multiplier = 1.0
            base_params['noise_strength'] = 0.03
            base_params['chromatic_aberration'] = 0.015
        
        # Apply multiplier to user parameters
        for key in ['high_freq_boost', 'texture_enhancement', 'edge_imperfection', 'compression_artifacts']:
            base_params[key] *= multiplier
            base_params[key] = min(base_params[key], 1.0)  # Cap at 1.0
        
        return base_params

    def _enhance_high_frequencies(self, img_array, strength):
        """Enhance high frequency components using FFT."""
        result = img_array.copy()
        
        for channel in range(img_array.shape[2]):
            # Apply FFT
            f_transform = np.fft.fft2(img_array[:, :, channel])
            f_shift = np.fft.fftshift(f_transform)
            
            # Create high-pass filter
            rows, cols = img_array.shape[:2]
            crow, ccol = rows // 2, cols // 2
            
            # Create frequency domain mask that enhances high frequencies
            mask = np.ones((rows, cols))
            radius = min(rows, cols) * 0.3  # Start enhancing from 30% of the radius
            
            y, x = np.ogrid[:rows, :cols]
            mask_area = ((x - ccol) ** 2 + (y - crow) ** 2) > radius ** 2
            mask[mask_area] = 1 + strength  # Boost high frequencies
            
            # Apply the mask
            f_shift_enhanced = f_shift * mask
            
            # Inverse FFT
            f_ishift = np.fft.ifftshift(f_shift_enhanced)
            img_back = np.fft.ifft2(f_ishift)
            img_back = np.abs(img_back)
            
            result[:, :, channel] = img_back
        
        return result

    def _add_realistic_noise(self, img_array, noise_type, strength, adaptive=True):
        """Add realistic noise patterns that mimic camera sensors or film grain."""
        height, width, channels = img_array.shape
        result = img_array.copy()
        
        if noise_type == "sensor":
            # Simulate camera sensor noise (shot noise + read noise)
            shot_noise = np.random.poisson(img_array * 255) / 255.0 - img_array
            read_noise = np.random.normal(0, 0.01, img_array.shape)
            noise = (shot_noise + read_noise) * strength
            
        elif noise_type == "film_grain":
            # Simulate film grain with frequency-dependent characteristics
            try:
                # Create grain at multiple scales for more realistic effect
                grain_size_1 = max(1, 2)  # Ensure minimum size of 1
                grain_size_2 = max(1, 4)  # Ensure minimum size of 1
                
                # Fine grain - ensure dimensions are valid
                fine_h, fine_w = max(1, height // grain_size_1), max(1, width // grain_size_1)
                fine_grain = np.random.random((fine_h, fine_w, channels))
                
                # Manually repeat instead of using kron
                fine_grain_expanded = np.repeat(np.repeat(fine_grain, grain_size_1, axis=0), grain_size_1, axis=1)
                fine_grain_expanded = fine_grain_expanded[:height, :width, :channels]
                
                # Coarse grain - ensure dimensions are valid
                coarse_h, coarse_w = max(1, height // grain_size_2), max(1, width // grain_size_2)
                coarse_grain = np.random.random((coarse_h, coarse_w, channels))
                
                # Manually repeat instead of using kron
                coarse_grain_expanded = np.repeat(np.repeat(coarse_grain, grain_size_2, axis=0), grain_size_2, axis=1)
                coarse_grain_expanded = coarse_grain_expanded[:height, :width, :channels]
                
                # Combine grains with different weights
                grain = fine_grain_expanded * 0.7 + coarse_grain_expanded * 0.3
                grain = (grain - 0.5) * strength * 3.0  # Reduced from testing value
                noise = grain
                
            except Exception as e:
                # Fallback to simple noise
                noise = np.random.normal(0, strength * 0.1, img_array.shape)
            
        elif noise_type == "gaussian":
            # Simple Gaussian noise
            noise = np.random.normal(0, strength * 0.15, img_array.shape)  # Increased from 0.05
            
        elif noise_type == "perlin":
            # Perlin-like noise for more natural patterns
            try:
                noise = self._generate_perlin_noise(height, width, channels, strength)
            except Exception as e:
                # Fallback to simple noise
                noise = np.random.normal(0, strength * 0.1, img_array.shape)
            
        else:  # mixed
            # Combine multiple noise types
            sensor_noise = np.random.poisson(img_array * 255) / 255.0 - img_array
            gaussian_noise = np.random.normal(0, strength * 0.08, img_array.shape)  # Increased from 0.03
            noise = (sensor_noise + gaussian_noise) * strength * 1.0  # Increased from 0.7
        
        # Apply adaptive noise based on image content
        if adaptive:
            # Reduce noise in very bright or very dark areas
            brightness = np.mean(img_array, axis=2, keepdims=True)
            adaptive_mask = 1 - np.abs(brightness - 0.5) * 2  # Less noise at extremes
            noise *= adaptive_mask
        
        result += noise
        return result

    def _enhance_textures(self, img_array, strength, adaptive=True):
        """Add micro-textures to smooth regions to break up AI-like smoothness."""
        # Detect smooth regions using variance
        gray = np.mean(img_array, axis=2)
        
        # Calculate local variance to find smooth areas
        from scipy.ndimage import uniform_filter
        local_mean = uniform_filter(gray, size=5)
        local_var = uniform_filter(gray**2, size=5) - local_mean**2
        
        # Create texture noise
        texture_noise = np.random.random(img_array.shape) - 0.5
        texture_noise *= strength * 0.02
        
        # Apply more texture to smoother regions
        smooth_mask = 1 / (1 + local_var * 100)  # Sigmoid to emphasize smooth regions
        smooth_mask = np.repeat(smooth_mask[:, :, np.newaxis], 3, axis=2)
        
        result = img_array + texture_noise * smooth_mask
        return result

    def _add_edge_imperfections(self, img_array, strength):
        """Add subtle imperfections to edges to make them less perfect."""
        # Detect edges using gradient
        gray = np.mean(img_array, axis=2)
        grad_x = np.gradient(gray, axis=1)
        grad_y = np.gradient(gray, axis=0)
        edge_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Create edge mask
        edge_mask = edge_magnitude > np.percentile(edge_magnitude, 80)
        edge_mask = np.repeat(edge_mask[:, :, np.newaxis], 3, axis=2)
        
        # Add subtle perturbations to edges
        perturbation = np.random.normal(0, strength * 0.01, img_array.shape)
        result = img_array + perturbation * edge_mask
        
        return result

    def _simulate_compression_artifacts(self, img_array, strength):
        """Simulate subtle JPEG-like compression artifacts."""
        # Convert to PIL for JPEG simulation
        img_pil = self._numpy_to_pil(img_array)
        
        # Simulate compression by saving and reloading with quality
        import io
        quality = max(85, int(100 - strength * 30))  # Quality between 70-95
        
        buffer = io.BytesIO()
        img_pil.save(buffer, format='JPEG', quality=quality)
        buffer.seek(0)
        compressed_img = Image.open(buffer)
        
        # Convert back to numpy
        result = self._pil_to_numpy(compressed_img)
        
        # Blend with original based on strength
        result = img_array * (1 - strength * 0.5) + result * (strength * 0.5)
        
        return result

    def _add_chromatic_aberration(self, img_array, strength):
        """Add subtle chromatic aberration effect."""
        if img_array.shape[2] < 3:
            return img_array
        
        height, width = img_array.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        # Create coordinate grids
        x, y = np.meshgrid(np.arange(width), np.arange(height))
        
        # Calculate distance from center
        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        
        # Create slight shift for red and blue channels
        shift_factor = strength * 2.0
        red_shift = dist / max_dist * shift_factor
        blue_shift = -dist / max_dist * shift_factor
        
        result = img_array.copy()
        
        # Apply shifts (simplified version)
        # In a full implementation, you'd use proper coordinate mapping
        shift_pixels = int(strength * 2)
        if shift_pixels > 0:
            # Red channel - slight outward shift
            result[:-shift_pixels, :-shift_pixels, 0] = img_array[shift_pixels:, shift_pixels:, 0]
            # Blue channel - slight inward shift  
            result[shift_pixels:, shift_pixels:, 2] = img_array[:-shift_pixels, :-shift_pixels, 2]
        
        return result

    def _preserve_quality(self, original, processed, threshold=0.95):
        """Preserve quality by blending with original where changes are too strong."""
        # Calculate difference
        diff = np.abs(processed - original)
        max_diff = np.max(diff, axis=2, keepdims=True)
        
        # Create blending mask - preserve more of original where diff is large
        blend_factor = np.where(max_diff > (1 - threshold), 
                               threshold + (1 - threshold) * 0.5, 
                               1.0)
        
        result = processed * blend_factor + original * (1 - blend_factor)
        return result

    def _generate_perlin_noise(self, height, width, channels, strength):
        """Generate Perlin-like noise pattern."""
        try:
            # Create multiple octaves for more realistic Perlin-like noise
            noise = np.zeros((height, width, channels))
            
            # Generate multiple scales of noise
            scales = [4, 8, 16, 32]
            weights = [0.5, 0.25, 0.15, 0.1]
            
            for scale, weight in zip(scales, weights):
                scale_h, scale_w = max(1, height // scale), max(1, width // scale)
                if scale_h > 0 and scale_w > 0:
                    # Generate noise at this scale
                    scale_noise = np.random.random((scale_h, scale_w, channels))
                    
                    # Upsample manually instead of using scipy
                    # Simple nearest neighbor upsampling
                    upsampled = np.repeat(np.repeat(scale_noise, scale, axis=0), scale, axis=1)
                    
                    # Ensure correct size
                    upsampled = upsampled[:height, :width, :channels]
                    
                    # Add to overall noise with weight
                    noise += upsampled * weight
            
            # Normalize and scale
            noise = (noise - 0.5) * strength * 2.0  # Reduced from testing value
            
            return noise
            
        except Exception as e:
            # Fallback to simple random noise
            fallback_noise = np.random.random((height, width, channels))
            fallback_noise = (fallback_noise - 0.5) * strength * 1.0
            return fallback_noise

    def _tensor_to_numpy(self, tensor):
        """Convert ComfyUI tensor to numpy array."""
        if isinstance(tensor, torch.Tensor):
            numpy_array = tensor.cpu().numpy()
        else:
            numpy_array = tensor
        
        # Handle different tensor shapes
        if len(numpy_array.shape) == 4:  # Batch dimension
            numpy_array = numpy_array[0]
        
        return numpy_array

    def _numpy_to_tensor(self, numpy_array):
        """Convert numpy array to ComfyUI tensor format."""
        # Ensure shape is [batch, height, width, channels]
        if len(numpy_array.shape) == 3:
            numpy_array = numpy_array[np.newaxis, ...]
        
        tensor = torch.from_numpy(numpy_array).float()
        return tensor

    def _numpy_to_pil(self, numpy_array):
        """Convert numpy array to PIL Image."""
        # Convert to 0-255 range
        img_uint8 = (numpy_array * 255).astype(np.uint8)
        return Image.fromarray(img_uint8)

    def _pil_to_numpy(self, pil_image):
        """Convert PIL Image to numpy array."""
        numpy_array = np.array(pil_image).astype(np.float32) / 255.0
        return numpy_array
