# Returns the width and height of an image.
class mbImageDimensions:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = (
        "INT",
        "INT",
    )
    RETURN_NAMES = (
        "width",
        "height",
    )
    FUNCTION = "get_size"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Returns the width and height of an image."

    def get_size(self, image):
        image_size = image.size()
        image_width = int(image_size[2])
        image_height = int(image_size[1])
        return (
            image_width,
            image_height,
        )


