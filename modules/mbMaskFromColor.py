"""
Mask from Color Node for ComfyUI
Generates a mask for pixels matching a specific color in an input image.
"""

# Standard library imports
import torch

# Local imports
from .common import CATEGORIES


class mbMaskFromColor:
    """Generate a mask for pixels matching a specific color in an input image."""
    
    # Class constants
    DEFAULT_COLOR = "#000000"
    DEFAULT_TOLERANCE = 0
    
    # Tolerance range for color matching
    TOLERANCE_RANGE = {"min": 0, "max": 255}
    
    def __init__(self):
        """Initialize the color mask node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types and validation."""
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image tensor to create mask from"
                }),
                "color": ("STRING", {
                    "default": cls.DEFAULT_COLOR,
                    "tooltip": "Target color in hex format (e.g., #FF0000 for red)"
                }),
                "tolerance": ("INT", {
                    "default": cls.DEFAULT_TOLERANCE,
                    **cls.TOLERANCE_RANGE,
                    "tooltip": "Tolerance for color matching (0 = exact match, higher = more permissive)"
                }),
            },
            "optional": {
            },
            "hidden": {
                "pick_color": ("STRING", {
                    "default": "Pick Color"
                }),
            }
        }

    # Node metadata
    TITLE = "Mask from Color"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)
    FUNCTION = "create_mask_from_color"
    CATEGORY = "unset"
    DESCRIPTION = "Generate a mask for pixels matching a specific color with optional tolerance."

    def create_mask_from_color(self, image, color, tolerance, pick_color=None):
        """
        Generate a mask for pixels matching the specified color.
        
        Args:
            image: Input image tensor in ComfyUI format [batch, height, width, channels]
            color: Target color in hex format (e.g., "#FF0000")
            tolerance: Color matching tolerance (0-255)
            pick_color: Hidden parameter for color picker button
            
        Returns:
            tuple: Generated mask tensor
        """
        try:
            # Parse the hex color to RGB values
            target_rgb = self._parse_hex_color(color)
            
            # Generate the mask
            mask = self._create_color_mask(image, target_rgb, tolerance)
            
            return (mask,)
            
        except Exception as e:
            raise RuntimeError(f"Color mask generation failed: {str(e)}")

    def _parse_hex_color(self, hex_color):
        """
        Parse hex color string to RGB values.
        
        Args:
            hex_color: Color in hex format (e.g., "#FF0000" or "FF0000")
            
        Returns:
            tuple: (r, g, b) values normalized to 0-1 range
        """
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Validate hex color format
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color format: {hex_color}. Expected format: #RRGGBB")
        
        try:
            # Parse hex to RGB (0-255 range)
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Normalize to 0-1 range (ComfyUI image format)
            return (r / 255.0, g / 255.0, b / 255.0)
            
        except ValueError:
            raise ValueError(f"Invalid hex color format: {hex_color}. Expected format: #RRGGBB")

    def _create_color_mask(self, image, target_rgb, tolerance):
        """
        Create a mask for pixels matching the target color within tolerance.
        
        Args:
            image: Input image tensor [batch, height, width, channels]
            target_rgb: Target RGB values in 0-1 range
            tolerance: Color matching tolerance (0-255, converted to 0-1 range)
            
        Returns:
            torch.Tensor: Mask tensor [batch, height, width]
        """
        # Convert tolerance from 0-255 range to 0-1 range
        tolerance_normalized = tolerance / 255.0
        
        # Extract RGB channels from image
        # Image format: [batch, height, width, channels]
        image_r = image[:, :, :, 0]
        image_g = image[:, :, :, 1] 
        image_b = image[:, :, :, 2]
        
        # Calculate absolute differences for each channel
        diff_r = torch.abs(image_r - target_rgb[0])
        diff_g = torch.abs(image_g - target_rgb[1])
        diff_b = torch.abs(image_b - target_rgb[2])
        
        # Create mask where all channels are within tolerance
        mask = (diff_r <= tolerance_normalized) & \
               (diff_g <= tolerance_normalized) & \
               (diff_b <= tolerance_normalized)
        
        # Convert boolean mask to float (0.0 or 1.0)
        mask = mask.float()
        
        return mask
