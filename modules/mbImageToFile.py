import os
import folder_paths
import numpy as np
from PIL import Image

# Saves an image to a file.
class mbImageToFile:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": ("IMAGE",),
                "base_name": ("STRING", {"default": "image"}),
                "id": ("INT", {"default": 0, "min": 0, "step": 1}),
                "use_id": (["yes", "no"], {"default": "no"}),
            },
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
    DESCRIPTION = "Saves an image to a file."

    def execute(self, image, base_name, id, use_id):
        prefix = folder_paths.get_input_directory().replace("\\", "/") + "/"
        os.makedirs(prefix, exist_ok=True)
    
        def save_image(img, filename):
            image_np = 255.0 * img.cpu().numpy().squeeze()
            image_pil = Image.fromarray(image_np.astype(np.uint8))
            image_pil.save(prefix + filename)
            print("Saved: " + prefix + filename)
    
        if image.shape[0] == 1:
            filename = f"{base_name}_{id}.png" if use_id == "yes" else f"{base_name}.png"
            save_image(image, filename)
        else:
            for i, img in enumerate(image):
                filename = f"{base_name}_{i}.png"
                save_image(img, filename)
    
        return (image, id)