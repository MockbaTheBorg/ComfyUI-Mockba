"""
An Image Preview node that saves a copy of the image to the temp folder.
"""

# Standard library imports
import json
import os
import random

# Third-party imports
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo

# ComfyUI imports
import folder_paths
from comfy.cli_args import args

# Local imports
from .common import CATEGORIES


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
                "images": ("IMAGE",),
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
    DESCRIPTION = "Previews and bridges the input images."
    OUTPUT_NODE = True

    def save_images(self, images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        """
        Saves the preview images to the temporary directory.

        Args:
            images: The images to save.
            filename_prefix: The prefix for the saved filenames.
            prompt: The prompt data to embed in the image metadata.
            extra_pnginfo: Extra PNG info to embed in the image metadata.

        Returns:
            A dictionary containing the UI data and the result tuple.
        """
        try:
            prefix_append = "_" + "".join(random.choice("abcdefghijklmnopqrstupvxyz") for _ in range(5))
            filename_prefix += prefix_append

            full_output_folder, filename, counter, subfolder, _ = folder_paths.get_save_image_path(
                filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0]
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
            return {"ui": {"images": []}, "result": (images,)}

