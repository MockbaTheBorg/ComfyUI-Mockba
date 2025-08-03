from .common import *

# Execute python code on inputs and return the result.
class mbExec:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "code": ("STRING", {"default": "out = i1", "multiline": True}),
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
        out = None
        
        # Remove hidden marker if present
        if code.startswith("# __HIDDEN__"):
            lines = code.split('\n')
            if len(lines) > 1:
                code = '\n'.join(lines[1:])  # Remove first line
            else:
                code = ""  # Only the marker was present
        
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
