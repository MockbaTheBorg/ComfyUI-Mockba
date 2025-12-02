"""
Select Node for ComfyUI
Selects one output from multiple inputs based on index selection.
"""

# Local imports
from .common import any_typ

class mbSelect:
    """Select one output from multiple inputs based on index."""
    
    def __init__(self):
        """Initialize the select node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for selection."""
        return {
            "required": {
                "input1": (any_typ, {
                    "tooltip": "First input option"
                }),
                "select": ("INT", {
                    "default": 1, 
                    "min": 1, 
                    "max": 9999999, 
                    "step": 1,
                    "tooltip": "Index of input to select (1-based)"
                })
            }
        }

    # Node metadata
    TITLE = "Input Selector"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("out",)
    FUNCTION = "select_input"
    CATEGORY = "unset"
    DESCRIPTION = "Select one output from multiple inputs based on index selection."

    def select_input(self, **kwargs):
        """
        Select input based on the specified index.
        
        Args:
            **kwargs: Contains 'select' index and variable number of inputs
            
        Returns:
            tuple: Selected input value or None if invalid selection
        """
        try:
            selected_index = int(kwargs["select"])
            input_name = f"input{selected_index}"

            if input_name in kwargs:
                selected_value = kwargs[input_name]
                return (selected_value,)
            else:
                print(f"mb Select: invalid selection index {selected_index} (no input{selected_index} found)")
                return (None,)
                
        except Exception as e:
            error_msg = f"Failed to select input: {str(e)}"
            print(error_msg)
            return (None,)


