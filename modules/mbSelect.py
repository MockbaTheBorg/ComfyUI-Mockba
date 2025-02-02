from .common import *

# Select an output from an arbitrary number of inputs
class mbSelect:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "select": ("INT", {"default": 1, "min": 1, "max": 100, "step": 1}),
            },
            "optional": {
                "input1": (any_typ,),
            },
            "hidden": {"unique_id": "UNIQUE_ID", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("out",)
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/tools"
    DESCRIPTION = "Select an output from an arbitrary number of inputs."

    def execute(self, *args, **kwargs):
        selected_index = int(kwargs["select"])
        input_name = f"input{selected_index}"

        if input_name in kwargs:
            return (kwargs[input_name],)
        else:
            print(f"mb Select: invalid selection (ignored)")
            return (None,)


