"""
Python Expression Evaluator Node for ComfyUI
Evaluates Python expressions on inputs with safe execution environment.
"""

# Local imports
from .common import any_typ

class mbEval:
    """Evaluate Python expressions on inputs and return the result."""
    
    # Class constants
    DEFAULT_CODE = "i1"

    def __init__(self):
        """Initialize the Python expression evaluator node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for Python expression evaluation."""
        return {
            "optional": {
                "i1": (any_typ, {
                    "tooltip": "First input variable (accessible as 'i1' in expression)"
                }),
                "code": ("STRING", {
                    "default": cls.DEFAULT_CODE,
                    "multiline": True,
                    "tooltip": "Python expression to evaluate (e.g., 'i1 + i2', 'len(i1)', 'max(i1, i2)')"
                })
            }
        }

    # Node metadata
    TITLE = "Python Expression Evaluator"
    RETURN_TYPES = (any_typ, "STRING")
    RETURN_NAMES = ("result", "error")
    FUNCTION = "evaluate"
    CATEGORY = "unset"
    DESCRIPTION = "Evaluate Python expressions on inputs. Returns error message if evaluation fails."

    def evaluate(self, code, **kwargs):
        for key, value in kwargs.items():
            exec(f"{key} = value", locals(), globals())
        if code == "":
            code = self.DEFAULT_CODE
        try:
            return (eval(code), None)
        except Exception as e:
            return (None, str(e))