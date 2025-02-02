import torch
import numpy as np
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageOps

# Generates a barcode image from a string
class mbBarcode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "data": ("STRING", {"default": "123456789"}),
                "type": (barcode.PROVIDED_BARCODES, {"default": "code128"}),
            }
        }

    RETURN_TYPES = (
        "IMAGE",
    )
    RETURN_NAMES = (
        "image",
    )
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/tools"
    DESCRIPTION = "Generates a barcode image from a string."
    
    def execute(self, data, type):
        code = barcode.get_barcode_class(type)
        my_barcode = code(data, writer=ImageWriter())
        image = my_barcode.render()

        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]

        return (image,)