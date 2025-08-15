"""
Value Display Node for ComfyUI
A node that displays any value in its title without outputs, created collapsed by default.
Supports custom Python formatting strings for value display.
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
            },
            "optional": {
                "format": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Python format string to format the value (e.g., '{:.2f}', '{:04d}', etc.). Leave empty for default formatting."
                })
            }
        }

    # Node metadata
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "display_value"
    CATEGORY = CATEGORIES["DEVELOPMENT"]
    DESCRIPTION = "Display any value in the node title without producing outputs. Supports custom Python formatting strings for value display. Useful for debugging and monitoring values in workflows."
    OUTPUT_NODE = True

    @classmethod
    def get_title(cls, value=None, format=None, **kwargs):
        """Return dynamic title based on input value."""
        if value is None:
            return "mbValue"
        
        # Handle different value types for display
        try:
            # Apply custom format if provided
            if format and format.strip():
                try:
                    formatted_value = format.format(value)
                    return f"mbValue: {formatted_value}"
                except (ValueError, TypeError, KeyError) as e:
                    # If formatting fails, show error and fallback to default
                    return f"mbValue: <format error: {str(e)}>"
            
            # Default formatting
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

    def display_value(self, value, format=None):
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
    def IS_CHANGED(cls, value, format=None, **kwargs):
        """Force update when value changes."""
        try:
            # Create a hash-like representation for change detection
            format_str = format or ""
            if isinstance(value, (int, float, str, bool)):
                return f"{str(value)}_{format_str}"
            elif hasattr(value, 'shape'):  # For tensors/arrays
                return f"{value.shape}_{hash(str(value.flatten()[:10]) if hasattr(value, 'flatten') else str(value))}_{format_str}"
            else:
                return f"{str(hash(str(value)))}_{format_str}"
        except Exception:
            import time
            return str(time.time())  # Fallback to timestamp
