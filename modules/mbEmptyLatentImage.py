import torch
import gc

MAX_RESOLUTION = 4096

# Creates an empty latent image using the cpu or gpu.
class mbEmptyLatentImage:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        devices = ["cpu", "cuda"]
        default_device = devices[0]

        resolutions = []
        with open("ComfyUI/custom_nodes/ComfyUI-Mockba/resolutions.txt", "r") as f:
            for line in f:
                resolutions.append(line.strip())
        default_resolution = resolutions[0]

        return {
            "required": {
                "size": (
                    resolutions,
                    {"default": default_resolution},
                ),
                "width": (
                    "INT",
                    {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8},
                ),
                "height": (
                    "INT",
                    {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8},
                ),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64}),
                "device": (devices, {"default": default_device}),
                "garbage_collect": (
                    "BOOLEAN",
                    {"default": False, "label_on": "enable", "label_off": "disable"},
                ),
            }
        }

    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent_image",)
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba"
    DESCRIPTION = "Creates an empty latent image using the cpu or gpu."

    def execute(self, size, width, height, batch_size, device, garbage_collect):
        if garbage_collect:
            gc.collect()
            if device.startswith("cuda"):
                torch.cuda.ipc_collect()
                torch.cuda.empty_cache()

        if size == "------":
            size = "custom"
        if size == "custom":
            n_width = width
            n_height = height
        else:
            n_width = int(size.split("x")[0])
            n_height = int(size.split("x")[1])

        latent = torch.zeros(
            [batch_size, 4, n_height // 8, n_width // 8], device=device
        )
        return (
            {
                "samples": latent,
            },
        )
