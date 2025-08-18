"""
Text Input Node for ComfyUI
Provides multiline text input with customizable default content.
"""

# Local imports
from .common import CATEGORIES


class mbText:
    """Multiline text input node for ComfyUI workflows."""
    
    # Class constants
    DEFAULT_TEXT = ""
    
    def __init__(self):
        """Initialize the text input node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for multiline text input."""
        return {
            "required": {
                "text": ("STRING", {
                    "default": cls.DEFAULT_TEXT, 
                    "multiline": True,
                    "tooltip": "Multiline text input for workflow processing"
                }),
            }
        }

    # Node metadata
    TITLE = "Multiline Text Input"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "get_text"
    CATEGORY = CATEGORIES["TEXT_PROCESSING"]
    DESCRIPTION = "Multiline text input node for entering and passing text through workflows."

    def get_text(self, text):
        """
        Return the input text as-is.
        
        Args:
            text: Input text string
            
        Returns:
            tuple: The input text unchanged
        """
        return (text,)
