import torch

# Rotates an image by 90, 180 or 270 degrees ccw.
class mbImageRotate:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": ("IMAGE",),
                "degrees": (["0", "90", "180", "270"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Rotates an image by 90, 180 or 270 degrees ccw."

    def execute(self, image, degrees):
        if degrees == "0":
            return (image,)

        def rotate_image(image_tensor, degrees):
            if degrees == "90":
                return torch.rot90(image_tensor, 1, [1, 2])
            elif degrees == "180":
                return torch.rot90(image_tensor, 2, [1, 2])
            elif degrees == "270":
                return torch.rot90(image_tensor, 3, [1, 2])

        rotated_image_tensor = torch.empty(0)
        for i in range(image.shape[0]):
            rotated_image_tensor = torch.cat(
                (rotated_image_tensor, rotate_image(image[i].unsqueeze(0), degrees)), dim=0
            )

        return (rotated_image_tensor,)


