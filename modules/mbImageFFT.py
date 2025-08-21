"""
Image FFT Analysis Node for ComfyUI
Computes and visualizes the Fast Fourier Transform of an image to detect AI generation patterns.
"""

# Standard library imports
import numpy as np
import torch

class mbImageFFT:
    """Compute and visualize the FFT of an image for AI detection analysis."""
    
    def __init__(self):
        """Initialize the image FFT analysis node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for FFT analysis."""
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image to analyze with FFT"
                }),
                "visualization_mode": (["magnitude", "log_magnitude", "phase", "power_spectrum"], {
                    "default": "log_magnitude",
                    "tooltip": "Type of FFT visualization to generate"
                }),
                "center_spectrum": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Center the frequency spectrum (move DC component to center)"
                }),
                "enhance_contrast": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enhance contrast for better visualization"
                }),
                "color_channel": (["all", "red", "green", "blue", "luminance"], {
                    "default": "luminance",
                    "tooltip": "Which color channel(s) to analyze"
                })
            },
            "optional": {
                "high_freq_threshold": ("FLOAT", {
                    "default": 0.1,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Threshold for highlighting high frequency components"
                })
            }
        }

    # Node metadata
    TITLE = "Image FFT Analysis"
    RETURN_TYPES = ("IMAGE", "IMAGE", "FLOAT", "STRING")
    RETURN_NAMES = ("fft_visualization", "original_image", "high_freq_ratio", "analysis_info")
    FUNCTION = "analyze_fft"
    CATEGORY = "unset"
    DESCRIPTION = "Analyze image FFT to detect patterns characteristic of AI-generated images. Shows frequency domain representation."

    def analyze_fft(self, image, visualization_mode="log_magnitude", center_spectrum=True, 
                   enhance_contrast=True, color_channel="luminance", high_freq_threshold=0.1):
        """
        Compute and visualize the FFT of an image.
        
        Args:
            image: Input image tensor
            visualization_mode: Type of FFT visualization
            center_spectrum: Whether to center the frequency spectrum
            enhance_contrast: Whether to enhance contrast
            color_channel: Which color channel to analyze
            high_freq_threshold: Threshold for high frequency analysis
            
        Returns:
            tuple: (fft_visualization, original_image, high_freq_ratio, analysis_info)
        """
        try:
            # Convert tensor to numpy array
            img_array = self._tensor_to_numpy(image)
            
            # Select color channel
            if color_channel == "luminance":
                # Convert to grayscale using standard luminance weights
                if img_array.shape[-1] >= 3:
                    gray_array = 0.299 * img_array[:, :, 0] + 0.587 * img_array[:, :, 1] + 0.114 * img_array[:, :, 2]
                else:
                    gray_array = img_array[:, :, 0]
            elif color_channel == "red":
                gray_array = img_array[:, :, 0]
            elif color_channel == "green":
                gray_array = img_array[:, :, 1] if img_array.shape[-1] > 1 else img_array[:, :, 0]
            elif color_channel == "blue":
                gray_array = img_array[:, :, 2] if img_array.shape[-1] > 2 else img_array[:, :, 0]
            else:  # "all" - process all channels and average
                if img_array.shape[-1] >= 3:
                    gray_array = np.mean(img_array[:, :, :3], axis=2)
                else:
                    gray_array = img_array[:, :, 0]
            
            # Compute 2D FFT
            fft_result = np.fft.fft2(gray_array)
            
            # Center the spectrum if requested
            if center_spectrum:
                fft_result = np.fft.fftshift(fft_result)
            
            # Generate visualization based on mode
            if visualization_mode == "magnitude":
                fft_vis = np.abs(fft_result)
            elif visualization_mode == "log_magnitude":
                fft_vis = np.log(np.abs(fft_result) + 1e-8)  # Add small epsilon to avoid log(0)
            elif visualization_mode == "phase":
                fft_vis = np.angle(fft_result)
            elif visualization_mode == "power_spectrum":
                fft_vis = np.abs(fft_result) ** 2
            
            # Normalize visualization to [0, 1]
            if visualization_mode == "phase":
                # Phase is already in [-pi, pi], normalize to [0, 1]
                fft_vis = (fft_vis + np.pi) / (2 * np.pi)
            else:
                fft_vis = self._normalize_array(fft_vis)
            
            # Enhance contrast if requested
            if enhance_contrast:
                fft_vis = self._enhance_contrast(fft_vis)
            
            # Convert back to RGB for display
            fft_rgb = np.stack([fft_vis, fft_vis, fft_vis], axis=-1)
            
            # Analyze high frequency content
            high_freq_ratio = self._analyze_high_frequencies(fft_result, high_freq_threshold)
            
            # Create analysis info
            analysis_info = self._create_analysis_info(
                fft_result, high_freq_ratio, visualization_mode, 
                color_channel, img_array.shape
            )
            
            # Convert back to tensor format
            fft_tensor = self._numpy_to_tensor(fft_rgb)
            
            print(f"FFT Analysis: {analysis_info}")
            
            return (fft_tensor, image, high_freq_ratio, analysis_info)
            
        except Exception as e:
            error_msg = f"FFT analysis failed: {str(e)}"
            print(error_msg)
            # Return original image and error info on failure
            return (image, image, 0.0, error_msg)

    def _tensor_to_numpy(self, tensor):
        """Convert ComfyUI image tensor to numpy array."""
        # tensor is typically [batch, height, width, channels]
        if tensor.dim() == 4:
            tensor = tensor[0]  # Take first image from batch
        
        # Convert to numpy and ensure proper range [0, 1]
        array = tensor.cpu().numpy()
        
        # Ensure values are in [0, 1] range
        if array.max() > 1.0:
            array = array / 255.0
        
        return array

    def _numpy_to_tensor(self, array):
        """Convert numpy array back to ComfyUI tensor format."""
        # Ensure proper shape [1, height, width, channels]
        if len(array.shape) == 2:
            array = np.expand_dims(array, axis=-1)
        if len(array.shape) == 3:
            array = np.expand_dims(array, axis=0)
        
        # Convert to tensor
        tensor = torch.from_numpy(array.astype(np.float32))
        return tensor

    def _normalize_array(self, array):
        """Normalize array to [0, 1] range."""
        min_val = np.min(array)
        max_val = np.max(array)
        if max_val > min_val:
            return (array - min_val) / (max_val - min_val)
        else:
            return np.zeros_like(array)

    def _enhance_contrast(self, array, percentile=2):
        """Enhance contrast using percentile stretching."""
        low = np.percentile(array, percentile)
        high = np.percentile(array, 100 - percentile)
        
        if high > low:
            enhanced = (array - low) / (high - low)
            enhanced = np.clip(enhanced, 0, 1)
            return enhanced
        else:
            return array

    def _analyze_high_frequencies(self, fft_result, threshold):
        """Analyze high frequency content in the FFT."""
        magnitude = np.abs(fft_result)
        
        # Create a mask for high frequencies (away from center)
        h, w = magnitude.shape
        center_y, center_x = h // 2, w // 2
        
        # Create distance matrix from center
        y, x = np.ogrid[:h, :w]
        distances = np.sqrt((y - center_y)**2 + (x - center_x)**2)
        
        # Normalize distances
        max_distance = np.sqrt(center_y**2 + center_x**2)
        normalized_distances = distances / max_distance
        
        # Define high frequency region (outer portion of spectrum)
        high_freq_mask = normalized_distances > threshold
        
        # Calculate ratio of high frequency energy
        total_energy = np.sum(magnitude**2)
        high_freq_energy = np.sum(magnitude[high_freq_mask]**2)
        
        if total_energy > 0:
            ratio = high_freq_energy / total_energy
        else:
            ratio = 0.0
        
        return float(ratio)

    def _create_analysis_info(self, fft_result, high_freq_ratio, vis_mode, channel, shape):
        """Create analysis information string."""
        magnitude = np.abs(fft_result)
        
        # Calculate some basic statistics
        dc_component = magnitude[0, 0] if not np.any(np.isnan(magnitude)) else 0
        max_magnitude = np.max(magnitude)
        mean_magnitude = np.mean(magnitude)
        
        info = f"FFT Analysis - Mode: {vis_mode}, Channel: {channel}, "
        info += f"Size: {shape[0]}x{shape[1]}, "
        info += f"High Freq Ratio: {high_freq_ratio:.4f}, "
        info += f"DC: {dc_component:.2f}, Max: {max_magnitude:.2f}, Mean: {mean_magnitude:.2f}"
        
        # Add interpretation hints
        if high_freq_ratio > 0.15:
            info += " [High frequency content - possible natural image]"
        elif high_freq_ratio < 0.05:
            info += " [Low frequency dominant - possible AI artifact]"
        else:
            info += " [Moderate frequency distribution]"
        
        return info

    @classmethod
    def IS_CHANGED(cls, image, visualization_mode, center_spectrum, enhance_contrast, color_channel, high_freq_threshold=0.1):
        """Check if inputs have changed to determine if node needs to re-execute."""
        # Always re-execute when image or parameters change
        return True
