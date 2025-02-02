from .common import *

# Execute python code on inputs and return the result.
class mbExec:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "code": ("STRING", {"default": "", "multiline": True}),
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

    def execute(self, code, *args, **kwargs):
        out = None
        if code == "":
            code = "out = i1"
        globals = {}
        for key, value in kwargs.items():
            globals[key] = value
        locals = {}
        exec(code, globals, locals)
        if "out" in locals:
            out = locals["out"]
        return (out,)
