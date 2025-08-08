"""
An Image Preview node that saves a copy of the image to the temp folder.
"""

# Standard library imports
import json
import os
import random

# Third-party imports
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo

# ComfyUI imports
import folder_paths
from comfy.cli_args import args

# Local imports
from .common import CATEGORIES, any_typ


class mbImagePreview:
    """
    A node to preview images and save them to a temporary directory.
    This node is also used as a bridge for images, allowing them to be used in
    multiple places in the workflow.
    """

    def __init__(self):
        """Initializes the node."""
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.compress_level = 1

    @classmethod
    def INPUT_TYPES(cls):
        """Defines the input types for the node."""
        return {
            "required": {
                "images": (any_typ,),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    # Node metadata
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "save_images"
    CATEGORY = CATEGORIES["IMAGE_PROCESSING"]
    DESCRIPTION = "Previews and bridges input images, creates dynamic-sized text images for non-tensor inputs, and displays masks as grayscale images."
    OUTPUT_NODE = True

    def create_text_image(self, text, font_size=20, margin=20, max_width=1200, min_width=100):
        """
        Creates an image with text content that automatically sizes to fit the text.
        
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

    def convert_to_tensor(self, img):
        """
        Converts a PIL Image to a tensor format expected by ComfyUI.
        
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

    def convert_mask_to_image(self, mask):
        """
        Converts a mask tensor to a grayscale image tensor.
        
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
        
        # Handle different mask dimensions
        if len(mask.shape) == 2:
            # 2D mask: add batch and channel dimensions
            mask = mask.unsqueeze(0).unsqueeze(-1)  # [H, W] -> [1, H, W, 1]
        elif len(mask.shape) == 3:
            if mask.shape[0] == 1:
                # [1, H, W] -> [1, H, W, 1]
                mask = mask.unsqueeze(-1)
            else:
                # [B, H, W] -> [B, H, W, 1]
                mask = mask.unsqueeze(-1)
        elif len(mask.shape) == 4 and mask.shape[-1] == 1:
            # Already in correct format [B, H, W, 1]
            pass
        else:
            # Flatten to 2D and treat as single mask
            mask = mask.view(-1, mask.shape[-1]).unsqueeze(0).unsqueeze(-1)
        
        # Convert to 3-channel grayscale (RGB with same values)
        grayscale_image = mask.repeat(1, 1, 1, 3)
        
        return grayscale_image

    def is_mask_tensor(self, data):
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

    def save_images(self, images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        """
        Saves the preview images to the temporary directory.
        Handles both tensor images and non-tensor inputs by creating text images.

        Args:
            images: The images to save or other data types to convert to text images.
            filename_prefix: The prefix for the saved filenames.
            prompt: The prompt data to embed in the image metadata.
            extra_pnginfo: Extra PNG info to embed in the image metadata.

        Returns:
            A dictionary containing the UI data and the result tuple.
        """
        try:
            # Check if images is a tensor (standard ComfyUI image format)
            is_tensor = hasattr(images, 'shape') and hasattr(images, 'cpu')
            
            if not is_tensor:
                # Convert non-tensor input to text image
                if isinstance(images, (list, tuple)):
                    # Handle lists/tuples by converting each element
                    text_content = ""
                    for i, item in enumerate(images):
                        text_content += f"Item {i+1}: {str(item)}\n"
                elif isinstance(images, dict):
                    # Handle dictionaries
                    text_content = "Dictionary contents:\n"
                    for key, value in images.items():
                        text_content += f"{key}: {str(value)}\n"
                else:
                    # Handle primitive types (string, int, float, etc.)
                    text_content = str(images)
                
                # Create text image with dynamic sizing
                text_img = self.create_text_image(text_content)
                
                # Convert to tensor format
                images = self.convert_to_tensor(text_img)
            elif is_tensor and self.is_mask_tensor(images):
                # Handle mask input - convert to grayscale image
                images = self.convert_mask_to_image(images)
            # If it's a regular image tensor, proceed normally without modification
            
            # Ensure images is always a list/batch
            if len(images.shape) == 3:  # Single image
                images = images.unsqueeze(0)
            
            prefix_append = "_" + "".join(random.choice("abcdefghijklmnopqrstupvxyz") for _ in range(5))
            filename_prefix += prefix_append

            full_output_folder, filename, counter, subfolder, _ = folder_paths.get_save_image_path(
                filename_prefix, self.output_dir, images[0].shape[2], images[0].shape[1]
            )

            results = []
            for batch_number, image in enumerate(images):
                img_array = 255.0 * image.cpu().numpy()
                img = Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))

                metadata = None
                if not args.disable_metadata:
                    metadata = PngInfo()
                    if prompt is not None:
                        metadata.add_text("prompt", json.dumps(prompt))
                    if extra_pnginfo is not None:
                        for key, value in extra_pnginfo.items():
                            metadata.add_text(key, json.dumps(value))

                filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
                file = f"{filename_with_batch_num}_{counter:05}_.png"
                img.save(
                    os.path.join(full_output_folder, file),
                    pnginfo=metadata,
                    compress_level=self.compress_level,
                )

                results.append({"filename": file, "subfolder": subfolder, "type": self.type})
                counter += 1

            return {"ui": {"images": results}, "result": (images,)}
        except Exception as e:
            print(f"Error saving image preview: {e}")
            # Return empty result instead of the original images to avoid further errors
            return {"ui": {"images": []}, "result": (torch.zeros((1, 512, 512, 3)),)}

