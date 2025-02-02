import torch
import numpy as np
from PIL import Image

# Converts an image to black and white using dithering
class mbImageDither:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "dither"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Converts an image to black and white using dithering."

    import torch
    from PIL import Image
    import numpy as np
    
    def dither(self, image):
        def convert_to_bw_tensor(image_tensor):
            image_np = 255.0 * image_tensor.cpu().numpy().squeeze()
            image_pil = Image.fromarray(image_np.astype(np.uint8))
            image_bw_pil = image_pil.convert("1")
            image_bw_np = np.array(image_bw_pil).astype(np.float32)
            return torch.from_numpy(image_bw_np).unsqueeze(0)

        bw_image_tensor = torch.empty(0)
        for i in range(image.shape[0]):
            bw_image_tensor = torch.cat((bw_image_tensor, convert_to_bw_tensor(image[i].unsqueeze(0))), dim=0)
    
        return (bw_image_tensor,)

