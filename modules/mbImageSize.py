# Shows image size information
class mbImageSize:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {"image": ("IMAGE",)},
            "hidden": {
                "width": ("INT",),
                "height": ("INT",),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT",)
    RETURN_NAMES = ("IMAGE", "width", "height",)
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Shows image size information."
    OUTPUT_NODE = True

    def execute(self, image, width=0, height=0):
        shape = image.shape
        width = shape[2]
        height = shape[1]
        return {
            "ui": {"width": [width], "height": [height]},
            "result": (
                image,
                width,
                height,
            ),
        }

