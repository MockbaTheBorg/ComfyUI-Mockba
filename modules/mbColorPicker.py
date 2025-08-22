"""
Color Picker Node for ComfyUI
Provides a color picker interface to select colors from images and output them in #RRGGBB format.
"""

class mbColorPicker:
    """Pick colors from images and output them in #RRGGBB format."""
    
    # Class constants
    DEFAULT_COLOR = "#000000"
    
    def __init__(self):
        """Initialize the color picker node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types and validation."""
        return {
            "required": {
                "color": ("STRING", {
                    "default": cls.DEFAULT_COLOR,
                    "tooltip": "Selected color in hex format (e.g., #FF0000 for red)"
                }),
            }
        }

    # Node metadata
    TITLE = "Color Picker"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("color",)
    FUNCTION = "output_color"
    CATEGORY = "unset"
    DESCRIPTION = "Pick colors from images using a visual color picker and output them in #RRGGBB format."

    def output_color(self, color):
        """
        Output the selected color in #RRGGBB format.
        
        Args:
            color: Selected color in hex format (e.g., "#FF0000")
            pick_color: Hidden parameter for color picker button
            
        Returns:
            tuple: Color in #RRGGBB format
        """
        try:
            # Validate and normalize the hex color format
            normalized_color = self._normalize_hex_color(color)
            
            return (normalized_color,)
            
        except Exception as e:
            # Return default color on error
            print(f"Color picker error: {str(e)}")
            return (self.DEFAULT_COLOR,)

    def _normalize_hex_color(self, hex_color):
        """
        Normalize hex color string to #RRGGBB format.
        
        Args:
            hex_color: Color in hex format (e.g., "#FF0000" or "FF0000")
            
        Returns:
            str: Normalized color in #RRGGBB format
        """
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Validate hex color format
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color format: {hex_color}. Expected format: RRGGBB")
        
        try:
            # Validate that it's actually hex
            int(hex_color, 16)
            
            # Return with # prefix
            return f"#{hex_color.upper()}"
            
        except ValueError:
            raise ValueError(f"Invalid hex color format: {hex_color}. Expected format: RRGGBB")
