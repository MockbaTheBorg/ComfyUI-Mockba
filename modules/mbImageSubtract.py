# Subtracts two images. Used to visually measure the difference between two images.
class mbImageSubtract:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "a": ("IMAGE",),
                "b": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = (
        "Subtracts two images. Used to measure the difference between two images."
    )

    def execute(self, a, b):
        return (abs(a - b),)


