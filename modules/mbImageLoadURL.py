import torch
import numpy as np
from PIL import Image, ImageOps

# Loads an image from an URL.
class mbImageLoadURL:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {"url": ("STRING", {"default": ""})},
        }

    RETURN_TYPES = (
        "IMAGE",
        "MASK",
    )
    RETURN_NAMES = (
        "image",
        "mask",
    )
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Loads an image from an URL."

    def execute(self, url):
        import requests
        from io import BytesIO

        response = requests.get(url)
        i = Image.open(BytesIO(response.content))
        i = ImageOps.exif_transpose(i)
        image = i.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        if "A" in i.getbands():
            mask = np.array(i.getchannel("A")).astype(np.float32) / 255.0
            mask = 1.0 - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
        return (image, mask.unsqueeze(0))


