from .common import *

# Select the first input that is not None.
class mbDemux:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "input1": (any_typ,),
            },
            "hidden": {"unique_id": "UNIQUE_ID", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("out",)
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/tools"
    DESCRIPTION = "Select the first input that is not None."

    def execute(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                return (value,)
        return (None,)
