"""
Signal Connector Node for ComfyUI
A simple passthrough node that connects any type of data from input to output.
"""

# Local imports
from .common import any_typ, CATEGORIES


class mbSignal:
    """Simple passthrough connector for any data type."""
    
    def __init__(self):
        """Initialize the signal connector node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for the signal connector."""
        return {
            "optional": {
                "input": (any_typ, {
                    "tooltip": "Any data type to pass through"
                }),
            }
        }

    # Node metadata
    TITLE = "Signal Connector"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("output",)
    FUNCTION = "passthrough"
    CATEGORY = "unset"
    DESCRIPTION = "Simple passthrough connector that forwards any input data to output without modification."

    def passthrough(self, input=None):
        """
        Pass the input data directly to output without any modification.
        
        Args:
            input: Any type of input data, or None if not connected
            
        Returns:
            tuple: The same input data as output, or None if no input
        """
        return (input,)