"""
String Input Node for ComfyUI
Provides single-line string input for workflow processing.
"""

# Local imports
from .common import CATEGORIES


class mbString:
    """Single-line string input node for ComfyUI workflows."""
    
    # Class constants
    DEFAULT_TEXT = ""
    
    def __init__(self):
        """Initialize the string input node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for single-line string input."""
        return {
            "required": {
                "text": ("STRING", {
                    "default": cls.DEFAULT_TEXT,
                    "multiline": False,
                    "tooltip": "Single-line text input for workflow processing"
                }),
            }
        }

    # Node metadata
    TITLE = "String Input"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "get_string"
    CATEGORY = CATEGORIES["TEXT_PROCESSING"]
    DESCRIPTION = "Single-line string input node for entering and passing text through workflows."

    def get_string(self, text):
        """
        Return the input string as-is.
        
        Args:
            text: Input text string
            
        Returns:
            tuple: The input text unchanged
        """
        return (text,)
