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
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngInfo

# ComfyUI imports
import folder_paths
from comfy.cli_args import args

# Local imports
from .common import (
    any_typ, 
    create_text_image, 
    convert_pil_to_tensor, 
    create_empty_mask,
    resize_mask_to_image,
    is_mask_tensor,
    load_mask_from_image,
    convert_mask_to_image_enhanced,
    create_empty_image_and_mask
)
from .common import tensor_to_pil_image

# Global cache for mask preservation functionality
preview_cache = {}
last_mask_cache = {}
image_id_map = {}
image_name_map = {}
pb_id_counter = 0


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
            "optional": {
                "restore_mask": (["never", "always", "if_same_size"], {"default": "never", "tooltip": "if_same_size: If the input image is the same size as the previous image, restore using the last saved mask\nalways: Whenever the input image changes, always restore using the last saved mask\nnever: Do not restore the mask"}),
            },
            "hidden": {
                "image": ("STRING", {"default": ""}),
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID"
            },
        }

    # Node metadata
    TITLE = "Image Preview"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "save_images"
    CATEGORY = "unset"
    DESCRIPTION = "Previews and bridges input images with mask support, creates dynamic-sized text images for non-tensor inputs, displays masks as grayscale images, and preserves masks between runs."
    OUTPUT_NODE = True

    def load_image_and_mask(self, image_id):
        """
        Loads an image and mask from an image ID, similar to bridge nodes.
        
        Args:
            image_id: String ID referencing a saved image
            
        Returns:
            tuple: (image_tensor, mask_tensor, ui_item) or None if failed
        """
        image_path = None
        
        # Check if this is a registered image ID
        if image_id not in image_id_map:
            return create_empty_image_and_mask()

        image_path = image_id_map[image_id]
        if not os.path.isfile(image_path):
            return create_empty_image_and_mask()

        try:
            i = Image.open(image_path)
            i = ImageOps.exif_transpose(i)
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]

            # Load mask using common function
            mask = load_mask_from_image(image_path)
            if mask is None:
                mask = create_empty_mask(64, 64)
            
            ui_item = {
                "filename": os.path.basename(image_path),
                "subfolder": "",
                "type": "temp"
            }
            
            return image, mask, ui_item
        except Exception as e:
            print(f"Error loading image and mask from {image_path}: {e}")
            return create_empty_image_and_mask()

    def get_cached_mask_path(self, node_id):
        """
        Get the path for storing cached mask for a node.
        
        Args:
            node_id: Unique node identifier
            
        Returns:
            str: Path to the cache file
        """
        cache_dir = os.path.join(self.output_dir, "mask_cache")
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, f"{node_id}_mask.pt")

    def load_cached_mask(self, node_id):
        """
        Load cached mask from file for persistence across workflow runs.
        
        Args:
            node_id: Unique node identifier
            
        Returns:
            torch.Tensor or None: Cached mask tensor or None if not found
        """
        cache_path = self.get_cached_mask_path(node_id)
        if os.path.isfile(cache_path):
            try:
                mask = torch.load(cache_path, map_location="cpu")
                print(f"Loaded cached mask for node {node_id}")
                return mask
            except Exception as e:
                print(f"Error loading cached mask: {e}")
        return None

    def save_cached_mask(self, node_id, mask):
        """
        Save mask to cache file for persistence across workflow runs.
        
        Args:
            node_id: Unique node identifier
            mask: Mask tensor to save
        """
        if mask is None or torch.all(mask == 0):
            return
            
        cache_path = self.get_cached_mask_path(node_id)
        try:
            torch.save(mask, cache_path)
            print(f"Saved cached mask for node {node_id}")
        except Exception as e:
            print(f"Error saving cached mask: {e}")

    def get_mask_for_images(self, images, restore_mask, unique_id):
        """
        Get the appropriate mask based on restore_mask setting and cached data.
        
        Args:
            images: Input image tensor
            restore_mask: Mask restoration setting ("never", "always", "if_same_size")
            unique_id: Unique node identifier
            
        Returns:
            tuple: (mask_tensor, should_save_cache) - mask to use and whether to save it
        """
        # Load cached mask from file (for persistence across workflow runs)
        cached_mask = self.load_cached_mask(unique_id) if unique_id else None
        
        if restore_mask == "never":
            # Never restore - always use empty mask, don't save
            return create_empty_mask(images.shape[1], images.shape[2]), False
        
        elif restore_mask == "always":
            # Always try to restore from cache
            if cached_mask is not None:
                # Use cached mask, don't overwrite it
                return resize_mask_to_image(cached_mask, images.shape), False
            else:
                # No cache exists, create empty and save it
                return create_empty_mask(images.shape[1], images.shape[2]), True
        
        elif restore_mask == "if_same_size":
            # Only restore if dimensions match
            if cached_mask is not None and cached_mask.shape[1:] == images.shape[1:3]:
                # Dimensions match, use cached mask but don't save (already cached)
                return cached_mask, False
            else:
                # Dimensions don't match or no cache, create empty and save it
                return create_empty_mask(images.shape[1], images.shape[2]), True
        
        # Fallback to empty mask, don't save
        return create_empty_mask(images.shape[1], images.shape[2]), False

    def register_clipspace_image(self, clipspace_path, node_id):
        """
        Register a clipspace image file in the preview bridge system.
        
        This handles the case where ComfyUI's mask editor creates clipspace files
        that need to be integrated with the preview bridge system.
        """
        # Remove [input] suffix if present
        clean_path = clipspace_path.replace(" [input]", "").replace("[input]", "")
        
        # Try to find the actual clipspace file
        input_dir = folder_paths.get_input_directory()
        potential_paths = [
            clean_path,
            os.path.join(input_dir, clean_path),
            os.path.join(input_dir, "clipspace", os.path.basename(clean_path)),
            os.path.abspath(clean_path),
        ]
        
        actual_file = None
        for path in potential_paths:
            if os.path.isfile(path):
                actual_file = path
                break
        
        if not actual_file:
            return False
            
        # Register it in our image_id_map
        image_id_map[clipspace_path] = actual_file
        
        return True

    def set_image_mapping(self, node_id, file_path, ui_item):
        """
        Sets up image mapping for preview bridge functionality.
        
        Args:
            node_id: Unique node identifier
            file_path: Path to the saved image file
            ui_item: UI item dictionary with file info
        """
        global pb_id_counter
        
        # Check if mapping already exists
        if (node_id, file_path) in image_name_map:
            pb_id, _ = image_name_map[node_id, file_path]
            return pb_id
        
        # Create new mapping
        pb_id = f"${node_id}-{pb_id_counter}"
        image_id_map[pb_id] = file_path
        image_name_map[node_id, file_path] = (pb_id, ui_item)
        
        # Load mask from alpha channel if present
        if os.path.isfile(file_path):
            try:
                mask = load_mask_from_image(file_path)
                if mask is not None:
                    last_mask_cache[node_id] = mask
            except Exception as e:
                print(f"Error loading mask from {file_path}: {e}")
        
        pb_id_counter += 1
        return pb_id

    def apply_mask_to_image(self, images, mask):
        """
        Applies a mask to images by adding alpha channel.
        
        Args:
            images: Input image tensor
            mask: Mask tensor to apply
            
        Returns:
            torch.Tensor: Images with alpha channel applied
        """
        if mask is None:
            return images
            
        # Resize mask to match image dimensions
        resized_mask = resize_mask_to_image(mask, images.shape)
        
        # Convert images to RGBA format
        batch_size = images.shape[0]
        height, width = images.shape[1], images.shape[2]
        
        # Create RGBA tensor
        rgba_images = torch.zeros((batch_size, height, width, 4), dtype=images.dtype, device=images.device)
        rgba_images[:, :, :, :3] = images  # Copy RGB channels
        
        # Apply mask as alpha channel (invert mask for proper alpha)
        for i in range(batch_size):
            if i < resized_mask.shape[0]:
                rgba_images[i, :, :, 3] = 1.0 - resized_mask[i]  # Invert mask for alpha
            else:
                rgba_images[i, :, :, 3] = 1.0  # Full opacity if no mask
        
        return rgba_images

    def save_images(self, images, image="", restore_mask="never", filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None, unique_id=None):
        """
        Saves the preview images to the temporary directory with mask support.
        Handles both tensor images and non-tensor inputs by creating text images.
        Follows the bridge node pattern for mask preservation.

        Args:
            images: The images to save or other data types to convert to text images.
            image: String ID for loading edited images with masks (from mask editor).
            restore_mask: How to handle mask restoration ("never", "always", "if_same_size").
            filename_prefix: The prefix for the saved filenames.
            prompt: The prompt data to embed in the image metadata.
            extra_pnginfo: Extra PNG info to embed in the image metadata.
            unique_id: Unique identifier for this node instance.

        Returns:
            A dictionary containing the UI data and the result tuple (images, mask).
        """
        try:
            need_refresh = False
            images_changed = False

            # Check if images have changed (this determines if we start fresh)
            if unique_id not in preview_cache:
                need_refresh = True
                images_changed = True
            elif preview_cache[unique_id][0] is not images:
                need_refresh = True
                images_changed = True

            # Handle clipspace files that aren't registered in the preview bridge system
            # This only applies when images haven't changed (same image, new mask scenario)
            if not need_refresh and image and image not in image_id_map:
                # Check if this is a clipspace file that needs to be registered
                is_clipspace = image and ("clipspace" in image.lower() or "[input]" in image)
                if is_clipspace:
                    if not self.register_clipspace_image(image, unique_id):
                        need_refresh = True
                else:
                    need_refresh = True

            # If we have an image ID and don't need refresh, load from saved image
            if not need_refresh and image:
                pixels, mask, path_item = self.load_image_and_mask(image)
                display_images = [path_item]
                should_save_cache = False  # Don't save when loading from existing image
            else:
                # Process the input images
                is_tensor = hasattr(images, 'shape') and hasattr(images, 'cpu')
                
                if not is_tensor:
                    # Convert non-tensor input to text image
                    if isinstance(images, (list, tuple)):
                        text_content = ""
                        for i, item in enumerate(images):
                            text_content += f"Item {i+1}: {str(item)}\n"
                    elif isinstance(images, dict):
                        text_content = "Dictionary contents:\n"
                        for key, value in images.items():
                            text_content += f"{key}: {str(value)}\n"
                    else:
                        text_content = str(images)
                    
                    text_img = create_text_image(text_content)
                    images = convert_pil_to_tensor(text_img)
                elif is_tensor and is_mask_tensor(images):
                    images = convert_mask_to_image_enhanced(images)
                
                # Ensure images is always a list/batch
                if len(images.shape) == 3:
                    images = images.unsqueeze(0)

                # Get the appropriate mask using simplified logic
                mask, should_save_cache = self.get_mask_for_images(images, restore_mask, unique_id)

                if mask is None:
                    mask = create_empty_mask(images.shape[1], images.shape[2])
                    # Save images without mask overlay
                    display_images = images
                else:
                    # Ensure mask matches image dimensions (double-check)
                    mask = resize_mask_to_image(mask, images.shape)
                    # Apply mask to images for display
                    display_images = self.apply_mask_to_image(images, mask)

                # Save the display images
                prefix_append = "_" + "".join(random.choice("abcdefghijklmnopqrstupvxyz") for _ in range(5))
                full_filename_prefix = filename_prefix + prefix_append

                full_output_folder, filename, counter, subfolder, _ = folder_paths.get_save_image_path(
                    full_filename_prefix, self.output_dir, display_images[0].shape[2], display_images[0].shape[1]
                )

                results = []
                for batch_number, display_image in enumerate(display_images):
                    # Use the shared helper to convert the tensor to a PIL image.
                    img = tensor_to_pil_image(display_image)

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

                    ui_item = {"filename": file, "subfolder": subfolder, "type": self.type}
                    results.append(ui_item)
                    counter += 1
                    
                    # Store image info for potential mask loading using proper mapping
                    if unique_id is not None:
                        image_path = os.path.join(full_output_folder, file)
                        pb_id = self.set_image_mapping(unique_id, image_path, ui_item)

                display_images = results
                pixels = images

                # Update cache with both images and results (like bridge nodes)
                preview_cache[unique_id] = (images, results)

            # Save the current mask to cache only when needed for persistence across workflow runs
            if unique_id is not None and should_save_cache:
                self.save_cached_mask(unique_id, mask)

            return {"ui": {"images": display_images}, "result": (pixels, mask)}
            
        except Exception as e:
            print(f"Error saving image preview: {e}")
            # Return empty result with default mask
            empty_mask = create_empty_mask()
            return {"ui": {"images": []}, "result": (torch.zeros((1, 512, 512, 3)), empty_mask)}

