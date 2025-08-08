"""
Demultiplexer Node for ComfyUI
Selects the first non-None input from multiple optional inputs.
"""

# Local imports
from .common import any_typ, CATEGORIES


class mbDemux:
    """Select the first non-None input from multiple optional inputs."""
    
    def __init__(self):
        """Initialize the demultiplexer node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for demultiplexing."""
        return {
            "optional": {
                "input1": (any_typ, {
                    "tooltip": "First optional input"
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID", 
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    # Node metadata
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("out",)
    FUNCTION = "demultiplex_inputs"
    CATEGORY = CATEGORIES["DATA_MANAGEMENT"]
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
                if self._is_valid_input(key, value):
                    return (value,)
                    
            # No valid inputs found
            print("mb Demux: No non-None inputs found")
            return (None,)
            
        except Exception as e:
            error_msg = f"Failed to demultiplex inputs: {str(e)}"
            print(error_msg)
            return (None,)

    def _is_valid_input(self, key, value):
        """Check if input is valid (not None and not a hidden parameter)."""
        # Skip hidden parameters
        if key in ["unique_id", "extra_pnginfo"]:
            return False
        
        # Check if value is not None
        return value is not None
