import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

# Centralized category definitions for all nodes
CATEGORIES = {
    "AI_TOOLS": "🖖 Mockba/ai",
    "DATA_MANAGEMENT": "🖖 Mockba/data",
    "DEVELOPMENT": "🖖 Mockba/development",
    "FILE_OPS": "🖖 Mockba/files", 
    "GENERATION": "🖖 Mockba/generation",
    "IMAGE_PROCESSING": "🖖 Mockba/image",
    "MASK_PROCESSING": "🖖 Mockba/mask",
    "TEXT_PROCESSING": "🖖 Mockba/text",
    "TOOLS": "🖖 Mockba/tools"
}

# A proxy class that always returns True when compared to any other object.
class AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False

any_typ = AlwaysEqualProxy("*")

# Functions
def mask_to_image(mask):
    """
    Converts a mask tensor to an image tensor format expected by ComfyUI.
    
    Takes a mask tensor and reshapes it to have 3 color channels (RGB) by expanding
    the single channel mask to all three channels, creating a grayscale image representation.
    
    Args:
        mask: Input mask tensor with shape [..., height, width]
        
    Returns:
        torch.Tensor: Image tensor with shape [batch, height, width, 3] where the mask
                     values are replicated across all 3 color channels
    """
    result = mask.reshape((-1, 1, mask.shape[-2], mask.shape[-1])).movedim(1, -1).expand(-1, -1, -1, 3)
    return result


def create_text_image(text, font_size=20, margin=20, max_width=1200, min_width=100):
    """
    Creates an image with text content that automatically sizes to fit the text.
    This is a global utility function used by multiple nodes.
    
    Args:
        text: The text to render in the image
        font_size: Font size for the text
        margin: Margin around the text
        max_width: Maximum width for the image
        min_width: Minimum width for the image (for very short text)
        
    Returns:
        PIL Image object
    """
    # Try to use a default font, fall back to default if not available
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Split text into lines, respecting existing newlines
    text_str = str(text)
    if '\n' in text_str:
        initial_lines = text_str.split('\n')
    else:
        initial_lines = [text_str]
    
    # Further split long lines to fit within max_width
    lines = []
    available_width = max_width - (2 * margin)
    
    for line in initial_lines:
        if not line:  # Handle empty lines
            lines.append("")
            continue
            
        words = line.split()
        if not words:
            lines.append("")
            continue
            
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= available_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
    
    # Calculate actual dimensions needed
    line_height = font_size + 5
    
    # Find the maximum line width
    max_line_width = 0
    for line in lines:
        if line:  # Skip empty lines for width calculation
            bbox = font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            max_line_width = max(max_line_width, line_width)
    
    # Calculate final image dimensions
    width = int(max(min_width, min(max_width, max_line_width + (2 * margin))))
    height = int(len(lines) * line_height + (2 * margin))
    
    # Create image with calculated dimensions
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw each line
    y_position = margin
    for line in lines:
        draw.text((margin, y_position), line, fill='black', font=font)
        y_position += line_height
    
    return img


def convert_pil_to_tensor(img):
    """
    Converts a PIL Image to a tensor format expected by ComfyUI.
    This is a global utility function used by multiple nodes.
    
    Args:
        img: PIL Image object
        
    Returns:
        torch.Tensor in the format expected by ComfyUI
    """
    # Convert PIL image to numpy array
    img_array = np.array(img).astype(np.float32) / 255.0
    
    # Convert to torch tensor and ensure correct dimensions [batch, height, width, channels]
    tensor = torch.from_numpy(img_array)
    if len(tensor.shape) == 3:
        tensor = tensor.unsqueeze(0)  # Add batch dimension
    
    return tensor


# Mask utility functions
def create_empty_mask(height=64, width=64):
    """
    Creates an empty mask tensor.
    
    Args:
        height: Height of the mask
        width: Width of the mask
        
    Returns:
        torch.Tensor: Empty mask tensor
    """
    return torch.zeros((1, height, width), dtype=torch.float32, device="cpu")


def resize_mask_to_image(mask, image_shape):
    """
    Resizes a mask to match the dimensions of an image.
    
    Args:
        mask: Input mask tensor
        image_shape: Target image shape (batch, height, width, channels)
        
    Returns:
        torch.Tensor: Resized mask tensor
    """
    if mask is None:
        return create_empty_mask(image_shape[1], image_shape[2])
        
    target_height, target_width = image_shape[1], image_shape[2]
    
    # Ensure mask has batch dimension
    if len(mask.shape) == 2:
        mask = mask.unsqueeze(0)
    
    # If mask already matches the target size, return as is
    if mask.shape[1] == target_height and mask.shape[2] == target_width:
        return mask
        
    # Resize mask using interpolation
    mask_4d = mask.unsqueeze(1)  # Add channel dimension for interpolation
    resized_mask = torch.nn.functional.interpolate(
        mask_4d, 
        size=(target_height, target_width), 
        mode="bilinear", 
        align_corners=False
    )
    return resized_mask.squeeze(1)  # Remove channel dimension


def is_mask_tensor(data):
    """
    Determines if the input data is a mask tensor.
    Masks are distinguished from regular images by having fewer dimensions or single channel.
    
    Args:
        data: Input data to check
        
    Returns:
        bool: True if data appears to be a mask tensor
    """
    if not hasattr(data, 'shape') or not hasattr(data, 'dtype'):
        return False
    
    # ComfyUI images are typically 4D [batch, height, width, 3_channels]
    # Masks are typically 2D [height, width], 3D [batch, height, width], or 4D [batch, height, width, 1]
    
    if len(data.shape) == 2:
        # 2D tensor is likely a mask
        return True
    elif len(data.shape) == 3:
        # 3D tensor without channel dimension is likely a mask
        return True
    elif len(data.shape) == 4:
        # 4D tensor with 1 channel is likely a mask
        # 4D tensor with 3 channels is likely a regular image
        if data.shape[-1] == 1:
            return True
        elif data.shape[-1] == 3:
            # This is likely a regular ComfyUI image tensor
            return False
        else:
            # Uncertain case, check value range as fallback
            if data.dtype in [torch.float32, torch.float64]:
                return data.min() >= 0 and data.max() <= 1.1
            elif data.dtype in [torch.uint8]:
                return data.min() >= 0 and data.max() <= 255
    
    return False


def load_mask_from_image(image_path):
    """
    Loads a mask from an image file's alpha channel.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        torch.Tensor: Mask tensor or None if no alpha channel
    """
    if not os.path.isfile(image_path):
        return None
        
    try:
        i = Image.open(image_path)
        i = ImageOps.exif_transpose(i)
        
        if 'A' in i.getbands():
            mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)  # Invert for ComfyUI format
            return mask.unsqueeze(0)  # Add batch dimension
    except Exception as e:
        print(f"Error loading mask from {image_path}: {e}")
        
    return None


def create_empty_image_and_mask(height=64, width=64):
    """
    Creates empty image and mask tensors for fallback scenarios.
    
    Args:
        height: Height of the tensors
        width: Width of the tensors
        
    Returns:
        tuple: (empty_image_tensor, empty_mask_tensor, ui_item)
    """
    empty_image = torch.zeros((1, height, width, 3), dtype=torch.float32)
    empty_mask = create_empty_mask(height, width)
    ui_item = {
        "filename": "empty.png",
        "subfolder": "",
        "type": "temp"
    }
    return empty_image, empty_mask, ui_item


def convert_mask_to_image_enhanced(mask):
    """
    Converts a mask tensor to a grayscale image tensor with enhanced preprocessing.
    This is an enhanced version of mask_to_image that handles more edge cases.
    
    Args:
        mask: Mask tensor (typically 2D or 3D)
        
    Returns:
        torch.Tensor in the format expected by ComfyUI (grayscale image)
    """
    # Ensure mask is a torch tensor
    if not isinstance(mask, torch.Tensor):
        mask = torch.tensor(mask, dtype=torch.float32)
    
    # Normalize mask values to 0-1 range if needed
    if mask.max() > 1.0:
        mask = mask / mask.max()
    
    # Ensure mask has the right dimensions for the global function
    # The global mask_to_image expects at least 3D tensor [batch, height, width]
    if len(mask.shape) == 2:
        # 2D mask: add batch dimension [H, W] -> [1, H, W]
        mask = mask.unsqueeze(0)
    elif len(mask.shape) == 4:
        # 4D mask: remove channel dimension if it's 1 [B, H, W, 1] -> [B, H, W]
        if mask.shape[-1] == 1:
            mask = mask.squeeze(-1)
    
    # Use the global mask_to_image function
    return mask_to_image(mask)

