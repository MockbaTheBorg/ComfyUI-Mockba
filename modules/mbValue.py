"""
Value Display Node for ComfyUI
A node that displays any value in its title without outputs, created collapsed by default.
Supports custom Python formatting strings for value display.
"""

# Local imports
from .common import any_typ

class mbValue:
    """Display any value in the node title without outputs."""
    
    def __init__(self):
        """Initialize the value display node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for value display."""
        return {
            "required": {
                "value": (any_typ, {
                    "tooltip": "Any value to display in the node title"
                })
            }
        }

    # Node metadata
    TITLE = "Value Display"
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "display_value"
    CATEGORY = "unset"
    DESCRIPTION = "Display any value in the node title without producing outputs. Supports custom Python formatting strings for value display. Useful for debugging and monitoring values in workflows."
    OUTPUT_NODE = True

    def display_value(self, value):
        """Process the input value (no output)."""        
        # Return the value in a format that JavaScript can access
        return {"ui": {"value": [value]}}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """Force execution every time by returning a unique value."""
        import time
        return time.time()
