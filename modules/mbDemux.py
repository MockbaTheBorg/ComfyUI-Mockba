"""
Demultiplexer Node for ComfyUI
Selects the first non-None input from multiple optional inputs.
"""

# Local imports
from .common import any_typ

class mbDemux:
    """Select the first non-None input from multiple optional inputs."""
    
    def __init__(self):
        """Initialize the demultiplexer node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for demultiplexing."""
        return {
            "required": {
                "input1": (any_typ, {
                    "tooltip": "First required input"
                }),
            }
        }

    # Node metadata
    TITLE = "Demultiplexer"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("out",)
    FUNCTION = "demultiplex_inputs"
    CATEGORY = "unset"
    DESCRIPTION = "Select the first non-None input from multiple optional inputs."

    def demultiplex_inputs(self, **kwargs):
        """
        Select the first non-None input from available inputs.
        
        Args:
            **kwargs: Variable number of optional inputs
            
        Returns:
            tuple: First non-None input value or None if all are None
        """
        try:
            # Iterate through inputs and return first non-None value
            for key, value in kwargs.items():
                if value is not None:
                    return (value,)
                    
            # No valid inputs found
            print("mb Demux: No non-None inputs found")
            return (None,)
            
        except Exception as e:
            error_msg = f"Failed to demultiplex inputs: {str(e)}"
            print(error_msg)
            return (None,)
