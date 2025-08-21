"""
JS based slider component for ComfyUI
Can be used to create responsive sliders for images and content.
"""

from .common import any_typ

class mbSlider:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "Xi": ("INT", {"default": 20, "min": -4294967296, "max": 4294967296}),
                "Xf": ("FLOAT", {"default": 20, "min": -4294967296, "max": 4294967296}),
                "isfloatX": ("INT", {"default": 0, "min": 0, "max": 1}),
            },
        }

    # Node metadata
    TITLE = "JS Slider"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("X",)
    FUNCTION = "slider"
    CATEGORY = "unset"
    DESCRIPTION = "JS based slider component for ComfyUI"

    def slider(self, Xi, Xf, isfloatX):
        if isfloatX > 0:
            out = Xf
        else:
            out = Xi
        return (out,)

