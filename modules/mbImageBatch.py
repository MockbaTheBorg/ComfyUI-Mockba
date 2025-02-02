import torch
import comfy.utils

# Creates a batch from an arbitrary number of images
class mbImageBatch:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image1": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "batch_image"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Creates a batch from an arbitrary number of images."

    def batch_image(self, **kwargs):
        image1 = kwargs["image1"]
        del kwargs["image1"]
        images = [value for value in kwargs.values()]

        if len(images) == 0:
            return (image1,)
        else:
            for image2 in images:
                if image1.shape[1:] != image2.shape[1:]:
                    image2 = comfy.utils.common_upscale(
                        image2.movedim(-1, 1),
                        image1.shape[2],
                        image1.shape[1],
                        "lanczos",
                        "center",
                    ).movedim(1, -1)
                image1 = torch.cat((image1, image2), dim=0)
            return (image1,)


