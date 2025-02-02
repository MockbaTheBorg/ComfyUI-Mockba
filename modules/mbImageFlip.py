import torch

# Flips an image horizontally or vertically.
class mbImageFlip:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": ("IMAGE",),
                "flip": (["none", "horizontal", "vertical", "both"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Flips an image horizontally or vertically."

    def execute(self, image, flip):
        if flip == "none":
            return (image,)

        def flip_image(image_tensor, flip):
            if flip == "horizontal":
                return torch.flip(image_tensor, [2])
            elif flip == "vertical":
                return torch.flip(image_tensor, [1])
            elif flip == "both":
                return torch.flip(image_tensor, [1, 2])

        flipped_image_tensor = torch.empty(0)
        for i in range(image.shape[0]):
            flipped_image_tensor = torch.cat(
                (flipped_image_tensor, flip_image(image[i].unsqueeze(0), flip)), dim=0
            )

        return (flipped_image_tensor,)
