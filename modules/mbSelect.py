"""
Select Node for ComfyUI
Selects one output from multiple inputs based on index selection.
"""

# Local imports
from .common import any_typ, CATEGORIES


class mbSelect:
    """Select one output from multiple inputs based on index."""
    
    # Class constants
    DEFAULT_SELECT = 1
    MIN_SELECT = 1
    MAX_SELECT = 100
    SELECT_STEP = 1
    
    def __init__(self):
        """Initialize the select node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for selection."""
        return {
            "required": {
                "select": ("INT", {
                    "default": cls.DEFAULT_SELECT, 
                    "min": cls.MIN_SELECT, 
                    "max": cls.MAX_SELECT, 
                    "step": cls.SELECT_STEP,
                    "tooltip": "Index of input to select (1-based)"
                }),
            },
            "optional": {
                "input1": (any_typ, {
                    "tooltip": "First input option"
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID", 
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
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


