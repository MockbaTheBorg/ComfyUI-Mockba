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
            },
            "hidden": {
                "format": ("STRING", {
                    "default": ""
                }),
                "show_type": ("BOOLEAN", {
                    "default": False
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

    def display_value(self, value, format="", show_type=False):
        """Process the input value (no output)."""
        # Apply custom format if provided
        display_value = value
        if format and format.strip():
            try:
                display_value = format.format(value)
            except (ValueError, TypeError, KeyError) as e:
                display_value = f"<format error: {str(e)}>"
        
        # Return the value in a format that JavaScript can access
        return {"ui": {"value": [display_value]}}

    @classmethod
    def IS_CHANGED(cls, value, format="", show_type=False, **kwargs):
        """Force update when value changes."""
        try:
            # Create a hash-like representation for change detection
            format_str = format or ""
            show_type_str = str(show_type)
            if isinstance(value, (int, float, str, bool)):
                return f"{str(value)}_{format_str}_{show_type_str}"
            elif hasattr(value, 'shape'):  # For tensors/arrays
                return f"{value.shape}_{hash(str(value.flatten()[:10]) if hasattr(value, 'flatten') else str(value))}_{format_str}_{show_type_str}"
            else:
                return f"{str(hash(str(value)))}_{format_str}_{show_type_str}"
        except Exception:
            import time
            return str(time.time())  # Fallback to timestamp
