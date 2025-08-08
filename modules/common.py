import torch

# Centralized category definitions for all nodes
CATEGORIES = {
    "IMAGE_PROCESSING": "🖖 Mockba/image",
    "FILE_OPS": "🖖 Mockba/files", 
    "TEXT_PROCESSING": "🖖 Mockba/text",
    "GENERATION": "🖖 Mockba/generation",
    "DATA_MANAGEMENT": "🖖 Mockba/data",
    "DEVELOPMENT": "🖖 Mockba/dev"
}

# A proxy class that always returns True when compared to any other object.
class AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False

any_typ = AlwaysEqualProxy("*")

# Functions
def mask_to_image(mask):
    result = mask.reshape((-1, 1, mask.shape[-2], mask.shape[-1])).movedim(1, -1).expand(-1, -1, -1, 3)
    return result

