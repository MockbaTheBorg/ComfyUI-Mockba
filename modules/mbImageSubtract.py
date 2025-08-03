import torch

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
                "mode": (["Difference Values", "Binary Difference"], {"default": "Difference Values"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = (
        "Subtracts two images. Mode options: 'Difference Values' shows the actual difference, "
        "'Binary Difference' shows black where no difference and white where there is difference."
    )

    def execute(self, a, b, mode):        
        # Calculate absolute difference
        diff = torch.abs(a - b)
        
        if mode == "Binary Difference":
            # Create binary mask: 0 (black) where no difference, 1 (white) where there is difference
            # Use a small threshold to account for floating point precision
            threshold = 1e-6
            binary_diff = (diff > threshold).float()
            return (binary_diff,)
        else:
            # Return actual difference values (clamped between 0 and 1)
            return (torch.clamp(diff, 0, 1),)


