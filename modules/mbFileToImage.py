import os
import folder_paths
import torch
import numpy as np
from PIL import Image, ImageOps

# Loads an image from a file.
class mbFileToImage:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "base_name": ("STRING", {"default": "image"}),
                "id": ("INT", {"default": 0, "min": 0, "step": 1}),
                "use_id": (["yes", "no"], {"default": "no"}),
            }
        }

    RETURN_TYPES = (
        "IMAGE",
        "INT",
    )
    RETURN_NAMES = (
        "image",
        "id",
    )
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/file"
    DESCRIPTION = "Loads an image from a file."
    
    def execute(self, base_name, id, use_id):
        prefix = folder_paths.get_input_directory().replace("\\", "/") + "/"
    
        def load_image(filename):
            image_pil = Image.open(filename).convert("RGB")
            image_np = np.array(image_pil).astype(np.float32) / 255.0
            return torch.from_numpy(image_np).permute(2, 0, 1).unsqueeze(0)
    
        if use_id == "no":
            filename = f"{prefix}{base_name}.png"
            if not os.path.exists(filename):
                return (torch.zeros(1, 512, 512, 3), id)
            image = load_image(filename).permute(0, 2, 3, 1)
        else:
            image = []
            i = 0
            while True:
                filename = f"{prefix}{base_name}_{i}.png"
                if not os.path.exists(filename):
                    break
                image.append(load_image(filename).permute(0, 2, 3, 1))
                i += 1
            if i == 0:
                return (torch.zeros(1, 512, 512, 3), id)
            image = torch.cat(image, dim=0)

        return (image, id)
