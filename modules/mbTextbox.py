"""
Dynamic Textbox Node for ComfyUI
Provides multiline text input with passthrough capability and screen output.
"""

# Local imports
from .common import CATEGORIES


class mbTextbox:
    """Dynamic textbox with passthrough capability and screen output."""
    
    # Class constants
    DEFAULT_TEXT = ""
    
    def __init__(self):
        """Initialize the dynamic textbox node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for dynamic textbox."""
        return {
            "required": {
                "text": ("STRING", {
                    "default": cls.DEFAULT_TEXT,
                    "multiline": True,
                    "forceInput": False,
                    "print_to_screen": True,
                    "tooltip": "Multiline text input with screen display"
                }),
            },
            "optional": {
                "passthrough": ("STRING", {
                    "default": cls.DEFAULT_TEXT, 
                    "multiline": True, 
                    "forceInput": True,
                    "tooltip": "Optional text input that overrides main text when provided"
                })
            },
        }

    # Node metadata
    TITLE = "Dynamic Textbox"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "process_textbox"
    CATEGORY = "unset"
    DESCRIPTION = "Dynamic textbox with passthrough capability and screen output functionality."
    OUTPUT_NODE = True

    def process_textbox(self, text="", passthrough=""):
        """
        Process textbox input with optional passthrough override.
        
        Args:
            text: Main text input
            passthrough: Optional text that overrides main text when provided
            
        Returns:
            dict or tuple: UI update with text display or simple text tuple
        """
        try:
            # Use passthrough text if provided, otherwise use main text
            final_text = self._determine_final_text(text, passthrough)
            
            # Return with UI update if passthrough was used
            if passthrough != "":
                return {
                    "ui": {"text": final_text}, 
                    "result": (final_text,)
                }
            else:
                return (final_text,)
                
        except Exception as e:
            error_msg = f"Failed to process textbox: {str(e)}"
            print(error_msg)
            return (text,)  # Fallback to original text

    def _determine_final_text(self, main_text, passthrough_text):
        """Determine which text to use based on passthrough availability."""
        return passthrough_text if passthrough_text != "" else main_text
