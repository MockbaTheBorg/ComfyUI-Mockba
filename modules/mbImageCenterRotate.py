"""
Image Center Rotation Node for ComfyUI
Rotates images by arbitrary floating-point angles around their center with options 
for cropping or expanding the output canvas.
"""

# Standard library imports
import torch
import math
import numpy as np
from PIL import Image
import torchvision.transforms.functional as TF

# Local imports
from .common import CATEGORIES


class mbImageCenterRotate:
    """Rotate images by arbitrary floating-point angles around their center."""
    
    # Class constants
    SIZE_MODE_OPTIONS = ["crop", "expand", "contract"]
    DEFAULT_SIZE_MODE = "crop"
    DEFAULT_ANGLE = 0.0
    DEFAULT_FILL_COLOR = "#000000"
    
    def __init__(self):
        """Initialize the image center rotation node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for image center rotation."""
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image tensor to rotate"
                }),
                "angle": ("FLOAT", {
                    "default": cls.DEFAULT_ANGLE,
                    "min": -360.0,
                    "max": 360.0,
                    "step": 0.1,
                    "tooltip": "Rotation angle in degrees (negative = counterclockwise, positive = clockwise)"
                }),
                "size_mode": (cls.SIZE_MODE_OPTIONS, {
                    "default": cls.DEFAULT_SIZE_MODE,
                    "tooltip": "crop: maintain size, expand: fit all content, contract: no empty areas"
                }),
                "fill_color": ("STRING", {
                    "default": cls.DEFAULT_FILL_COLOR,
                    "tooltip": "Fill color for empty areas in #RRGGBB format (e.g., #000000 for black, #FFFFFF for white)"
                }),
            }
        }

    # Node metadata
    TITLE = "Image Center Rotate"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "rotate_image"
    CATEGORY = CATEGORIES["IMAGE_PROCESSING"]
    DESCRIPTION = "Rotate images by arbitrary floating-point angles around their center with crop, expand, or contract options. Returns inverted mask for outpainting."

    def rotate_image(self, image, angle, size_mode, fill_color):
        """
        Rotate image by specified angle around its center.
        
        Args:
            image: Input image tensor in ComfyUI format [batch, height, width, channels]
            angle: Rotation angle in degrees (negative = counterclockwise, positive = clockwise)
            size_mode: "crop" to maintain original size, "expand" to fit rotated image, "contract" to remove empty areas
            fill_color: Fill color in #RRGGBB format (e.g., "#000000" for black)
            
        Returns:
            tuple: (rotated image tensor, inverted mask tensor for outpainting)
        """
        # Early return for zero rotation
        if abs(angle) < 1e-6:
            batch_size, height, width, channels = image.shape
            # Create inverted mask (0 = original image area, 1 = fill area for outpainting)
            mask = torch.zeros((batch_size, height, width), dtype=torch.float32, device=image.device)
            return (image, mask)

        try:
            rotated_image, mask = self._apply_rotation_transform(image, angle, size_mode, fill_color)
            return (rotated_image, mask)
            
        except Exception as e:
            error_msg = f"Failed to rotate image: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)

    def _apply_rotation_transform(self, image_tensor, angle, size_mode, fill_color):
        """Apply rotation transformation to the entire batch."""
        batch_size, height, width, channels = image_tensor.shape
        device = image_tensor.device
        
        # Convert to PIL format for processing
        rotated_images = []
        masks = []
        
        # Parse hex color to RGB values
        fill_rgb = self._parse_hex_color(fill_color)
        
        for i in range(batch_size):
            # Convert tensor to PIL Image (0-1 range to 0-255)
            img_np = (image_tensor[i].cpu().numpy() * 255).astype(np.uint8)
            pil_img = Image.fromarray(img_np)
            
            if size_mode == "crop":
                # Rotate and crop to original size (invert angle for correct direction)
                rotated_pil = pil_img.rotate(
                    -angle, 
                    resample=Image.BICUBIC, 
                    expand=False,
                    fillcolor=fill_rgb
                )
                # For cropped mode, create a mask that shows which areas are fill (for outpainting)
                mask = self._create_crop_mask(height, width, angle, device)
                
            elif size_mode == "expand":
                # Rotate and expand canvas to fit (invert angle for correct direction)
                rotated_pil = pil_img.rotate(
                    -angle, 
                    resample=Image.BICUBIC, 
                    expand=True,
                    fillcolor=fill_rgb
                )
                # For expanded mode, create a mask that shows the fill areas (for outpainting)
                mask = self._create_expand_mask(height, width, angle, rotated_pil.size, device)
                
            else:  # contract
                # Rotate and expand first, then crop to remove empty areas
                rotated_pil = pil_img.rotate(
                    -angle, 
                    resample=Image.BICUBIC, 
                    expand=True,
                    fillcolor=fill_rgb
                )
                # Contract to remove empty areas and create corresponding mask
                rotated_pil, mask = self._create_contract_result(height, width, angle, rotated_pil, device)
            
            # Convert back to tensor format
            rotated_np = np.array(rotated_pil).astype(np.float32) / 255.0
            rotated_tensor = torch.from_numpy(rotated_np).to(device)
            
            rotated_images.append(rotated_tensor)
            masks.append(mask)
        
        # Stack all images and masks
        final_images = torch.stack(rotated_images, dim=0)
        final_masks = torch.stack(masks, dim=0)
        
        return final_images, final_masks

    def _parse_hex_color(self, hex_color):
        """Parse hex color string to RGB tuple."""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Ensure it's 6 characters
            if len(hex_color) != 6:
                hex_color = "000000"  # Default to black
            
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            return (r, g, b)
        except:
            return (0, 0, 0)  # Default to black on error

    def _create_crop_mask(self, height, width, angle, device):
        """Create an inverted mask for cropped rotation showing fill areas for outpainting."""
        # Convert angle to radians (invert for correct coordinate transformation)
        angle_rad = math.radians(-angle)
        
        # Calculate the effective crop region after rotation
        cos_a = abs(math.cos(angle_rad))
        sin_a = abs(math.sin(angle_rad))
        
        # Calculate how much the corners are cut off
        # This is an approximation for the visible area after rotation
        effective_width = width * cos_a + height * sin_a
        effective_height = height * cos_a + width * sin_a
        
        # Calculate the scale factor to fit the rotated image back into original dimensions
        scale_w = width / effective_width if effective_width > 0 else 1.0
        scale_h = height / effective_height if effective_height > 0 else 1.0
        scale = min(scale_w, scale_h)
        
        # Create a mask that represents the fill areas (inverted for outpainting)
        mask = torch.zeros((height, width), dtype=torch.float32, device=device)
        
        if scale < 1.0:
            # Calculate the region that might have fill values
            center_x, center_y = width // 2, height // 2
            
            # Create coordinates grid
            y_coords, x_coords = torch.meshgrid(
                torch.arange(height, dtype=torch.float32, device=device),
                torch.arange(width, dtype=torch.float32, device=device),
                indexing='ij'
            )
            
            # Center coordinates
            x_centered = x_coords - center_x
            y_centered = y_coords - center_y
            
            # Rotate coordinates in the same direction as the image rotation
            cos_pos = math.cos(angle_rad)
            sin_pos = math.sin(angle_rad)
            
            x_rotated = x_centered * cos_pos - y_centered * sin_pos
            y_rotated = x_centered * sin_pos + y_centered * cos_pos
            
            # Check if rotated coordinates are outside original image bounds
            invalid_mask = (
                (abs(x_rotated) > width / 2) | 
                (abs(y_rotated) > height / 2)
            )
            
            # Inverted mask: 1 for fill areas, 0 for original image areas
            mask = invalid_mask.float()
        
        return mask

    def _create_contract_result(self, orig_height, orig_width, angle, rotated_pil, device):
        """Create contracted image and mask by cropping to remove all empty areas."""
        new_width, new_height = rotated_pil.size
        
        # Convert angle to radians (invert for correct coordinate transformation)
        angle_rad = math.radians(-angle)
        
        # Calculate the maximum rectangle that fits inside the rotated image without empty areas
        # This is the inscribed rectangle of the original image after rotation
        cos_a = abs(math.cos(angle_rad))
        sin_a = abs(math.sin(angle_rad))
        
        # Calculate the dimensions of the largest rectangle that fits entirely within the rotated original image
        # Using the formula for inscribed rectangle in a rotated rectangle
        if cos_a == 0:  # 90 or 270 degrees
            contracted_width = orig_height
            contracted_height = orig_width
        elif sin_a == 0:  # 0 or 180 degrees
            contracted_width = orig_width
            contracted_height = orig_height
        else:
            # For other angles, calculate the inscribed rectangle
            # This ensures no fill areas are visible
            w_factor = (orig_width * cos_a + orig_height * sin_a)
            h_factor = (orig_height * cos_a + orig_width * sin_a)
            
            # The contracted dimensions are the original dimensions scaled down
            # to fit entirely within the rotated bounds
            scale_w = orig_width / w_factor
            scale_h = orig_height / h_factor
            scale = min(scale_w, scale_h)
            
            contracted_width = int(orig_width * scale)
            contracted_height = int(orig_height * scale)
        
        # Ensure minimum size
        contracted_width = max(1, contracted_width)
        contracted_height = max(1, contracted_height)
        
        # Calculate crop bounds centered in the expanded image
        left = (new_width - contracted_width) // 2
        top = (new_height - contracted_height) // 2
        right = left + contracted_width
        bottom = top + contracted_height
        
        # Crop the image to remove empty areas
        contracted_pil = rotated_pil.crop((left, top, right, bottom))
        
        # For contract mode, there should be no empty areas, so mask is all zeros
        mask = torch.zeros((contracted_height, contracted_width), dtype=torch.float32, device=device)
        
        return contracted_pil, mask

    def _create_expand_mask(self, orig_height, orig_width, angle, new_size, device):
        """Create an inverted mask for expanded rotation showing fill areas for outpainting."""
        new_width, new_height = new_size
        
        # Create mask with new dimensions - start with all fill areas
        mask = torch.ones((new_height, new_width), dtype=torch.float32, device=device)
        
        # Calculate the offset of the original image in the expanded canvas
        offset_x = (new_width - orig_width) // 2
        offset_y = (new_height - orig_height) // 2
        
        # Convert angle to radians (invert for correct coordinate transformation)
        angle_rad = math.radians(-angle)
        center_x = new_width / 2
        center_y = new_height / 2
        
        # Create coordinate grids for the new image
        y_coords, x_coords = torch.meshgrid(
            torch.arange(new_height, dtype=torch.float32, device=device),
            torch.arange(new_width, dtype=torch.float32, device=device),
            indexing='ij'
        )
        
        # Center coordinates
        x_centered = x_coords - center_x
        y_centered = y_coords - center_y
        
        # Rotate coordinates in the same direction as the image rotation to find original areas
        cos_pos = math.cos(angle_rad)
        sin_pos = math.sin(angle_rad)
        
        x_rotated = x_centered * cos_pos - y_centered * sin_pos + center_x
        y_rotated = x_centered * sin_pos + y_centered * cos_pos + center_y
        
        # Check if rotated coordinates correspond to original image area
        # Account for the offset in the expanded canvas
        orig_left = offset_x
        orig_right = offset_x + orig_width
        orig_top = offset_y
        orig_bottom = offset_y + orig_height
        
        original_area_mask = (
            (x_rotated >= orig_left) & (x_rotated < orig_right) &
            (y_rotated >= orig_top) & (y_rotated < orig_bottom)
        )
        
        # Inverted mask: 0 for original image areas, 1 for fill areas
        mask = (~original_area_mask).float()
        
        return mask
