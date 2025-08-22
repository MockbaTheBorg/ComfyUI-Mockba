"""
End plug to force execution
A simple node that has no outputs, does nothing, and is always executed.
Used as an endpoint to force the execution of upstream nodes.
"""

# Local imports
from .common import any_typ

class mbEnd:
    """Simple end node that does nothing"""
    
    def __init__(self):
        """Initialize the end node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types."""
        return {
            "required": {
                "input": (any_typ, {
                    "tooltip": "Any type of data"
                }),
            },
        }

    # Node metadata
    TITLE = "End Point"
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "end"
    CATEGORY = "unset"
    DESCRIPTION = "Simple end node that does nothing and is always executed."
    OUTPUT_NODE = True

    def end(self, **kwargs):
        """
        Does nothing - this is just an end point to force execution.
        
        Args:
            input: Any type of input data, or None if not connected
            
        Returns:
            None: No output as this is an end node
        """
        return (None,)