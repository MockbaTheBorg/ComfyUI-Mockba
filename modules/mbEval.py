from .common import *

# Evaluate a python expression on inputs and return the result.
class mbEval:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "code": ("STRING", {"default": ""}),
            },
            "optional": {
                "i1": (any_typ,),
            }
        }

    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("out",)
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/tools"
    DESCRIPTION = "Evaluate a python expression on inputs and return the result."

    def execute(self, code, **kwargs):
        for key, value in kwargs.items():
            exec(f"{key} = value")
        if code == "":
            code = "i1"
        return (eval(code),)


