"""
Python Code Executor Node for ComfyUI
Executes Python code with inputs and returns the result through 'out' variable.
"""

# Local imports
from .common import any_typ

class mbExec:
    """Execute Python code on inputs and return the result via 'out' variable."""
    
    # Class constants
    DEFAULT_CODE = "out = i1"
    
    def __init__(self):
        """Initialize the Python code executor node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for Python code execution."""
        return {
            "optional": {
                "i1": (any_typ, {
                    "tooltip": "First input variable (accessible as 'i1' in code)"
                }),
                "code": ("STRING", {
                    "default": cls.DEFAULT_CODE,
                    "multiline": True,
                    "tooltip": "Python code to execute. Set 'out' variable to return result (e.g., 'out = i1 + i2')"
                })
            }
        }

    # Node metadata
    TITLE = "Python Code Executor"
    RETURN_TYPES = (any_typ, "STRING")
    RETURN_NAMES = ("out", "error")
    FUNCTION = "execute"
    CATEGORY = "unset"
    DESCRIPTION = "Execute Python code on inputs. Set 'out' variable to return result. Returns error message if execution fails."

    def execute(self, code, **kwargs):
        out = None
        error = None
        if code == "":
            code = self.DEFAULT_CODE
        globals = {}
        for key, value in kwargs.items():
            globals[key] = value
        locals = {}
        try:
            exec(code, globals, locals)
        except Exception as e:
            error = str(e)
        if "out" in locals:
            out = locals["out"]
        return (out, error)

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """Force execution every time by returning a unique value."""
        import random
        return random.randint(0, 32768)
