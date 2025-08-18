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
from PIL import Image
from PIL.PngImagePlugin import PngInfo

# ComfyUI imports
import folder_paths
from comfy.cli_args import args

# Local imports
from .common import CATEGORIES, any_typ, create_text_image, convert_pil_to_tensor, mask_to_image


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
    TITLE = "Image Preview"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "save_images"
    CATEGORY = "unset"
    DESCRIPTION = "Previews and bridges input images, creates dynamic-sized text images for non-tensor inputs, and displays masks as grayscale images."
    OUTPUT_NODE = True

    def convert_mask_to_image(self, mask):
        """
        Converts a mask tensor to a grayscale image tensor using global utility.
        
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
        grayscale_image = mask_to_image(mask)
        
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
                text_img = create_text_image(text_content)
                
                # Convert to tensor format
                images = convert_pil_to_tensor(text_img)
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

