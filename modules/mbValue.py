"""
Value Display Node for ComfyUI
A node that displays any value in its title without outputs, created collapsed by default.
"""

# Local imports
from .common import CATEGORIES, any_typ


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
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "display_value"
    CATEGORY = CATEGORIES["DEVELOPMENT"]
    DESCRIPTION = "Display any value in the node title without producing outputs. Useful for debugging and monitoring values in workflows."
    OUTPUT_NODE = True

    @classmethod
    def get_title(cls, value=None, **kwargs):
        """Return dynamic title based on input value."""
        if value is None:
            return "mbValue"
        
        # Handle different value types for display
        try:
            if isinstance(value, (int, float)):
                return f"mbValue: {value}"
            elif isinstance(value, str):
                # Truncate long strings
                display_str = value[:30] + "..." if len(value) > 30 else value
                return f"mbValue: {display_str}"
            elif isinstance(value, (list, tuple)):
                return f"mbValue: [{len(value)} items]"
            elif hasattr(value, 'shape'):  # For tensors/arrays
                return f"mbValue: {value.shape}"
            else:
                # For other types, show type name
                type_name = type(value).__name__
                return f"mbValue: <{type_name}>"
        except Exception:
            return "mbValue: <unknown>"

    def display_value(self, value):
        """Process the input value (no output)."""
        # Return the value in a format that JavaScript can access
        return {"ui": {"value": [value]}}

    @classmethod
    def IS_CHANGED(cls, value, **kwargs):
        """Force update when value changes."""
        try:
            # Create a hash-like representation for change detection
            if isinstance(value, (int, float, str, bool)):
                return str(value)
            elif hasattr(value, 'shape'):  # For tensors/arrays
                return f"{value.shape}_{hash(str(value.flatten()[:10]) if hasattr(value, 'flatten') else str(value))}"
            else:
                return str(hash(str(value)))
        except Exception:
            import time
            return str(time.time())  # Fallback to timestamp
