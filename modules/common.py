import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Centralized category definitions for all nodes
CATEGORIES = {
    "DATA_MANAGEMENT": "🖖 Mockba/data",
    "DEVELOPMENT": "🖖 Mockba/development",
    "FILE_OPS": "🖖 Mockba/files", 
    "GENERATION": "🖖 Mockba/generation",
    "IMAGE_PROCESSING": "🖖 Mockba/image",
    "MASK_PROCESSING": "🖖 Mockba/mask",
    "TEXT_PROCESSING": "🖖 Mockba/text"
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
    width = max(min_width, min(max_width, max_line_width + (2 * margin)))
    height = len(lines) * line_height + (2 * margin)
    
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

