"""
Barcode Generation Node for ComfyUI
Generates various barcode formats from text input with customizable styling.
"""

# Third-party imports
import barcode
from barcode.writer import ImageWriter

# Local imports
from .common import CATEGORIES, convert_pil_to_tensor


class mbBarcode:
    """Generate barcode images from text data with various format options."""
    
    # Class constants
    DEFAULT_DATA = "123456789"
    DEFAULT_TYPE = "code128"
    DEFAULT_FONT_SIZE = 10
    DEFAULT_TEXT_DISTANCE = 4
    
    # Input validation ranges
    FONT_SIZE_RANGE = {"min": 8, "max": 72}
    TEXT_DISTANCE_RANGE = {"min": 1, "max": 20}
    
    def __init__(self):
        """Initialize the barcode generator node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types and validation."""
        return {
            "required": {
                "data": ("STRING", {
                    "default": cls.DEFAULT_DATA,
                    "tooltip": "Text data to encode in barcode"
                }),
                "type": (barcode.PROVIDED_BARCODES, {
                    "default": cls.DEFAULT_TYPE,
                    "tooltip": "Barcode format type"
                }),
                "fontsize": ("INT", {
                    "default": cls.DEFAULT_FONT_SIZE,
                    **cls.FONT_SIZE_RANGE,
                    "tooltip": "Font size for barcode text"
                }),
                "textdistance": ("INT", {
                    "default": cls.DEFAULT_TEXT_DISTANCE,
                    **cls.TEXT_DISTANCE_RANGE,
                    "tooltip": "Distance between barcode and text"
                }),
            }
        }

    # Node metadata
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_barcode"
    CATEGORY = CATEGORIES["GENERATION"]
    DESCRIPTION = "Generate barcode images from text with customizable formatting options."

    def generate_barcode(self, data, type, fontsize, textdistance):
        """
        Generate a barcode image from input data.
        
        Args:
            data: Text to encode
            type: Barcode format
            fontsize: Font size for text
            textdistance: Space between barcode and text
            
        Returns:
            tuple: Generated barcode image as tensor
        """
        try:
            # Generate barcode
            barcode_image = self._create_barcode(data, type, fontsize, textdistance)
            
            # Convert to ComfyUI tensor format
            tensor_image = convert_pil_to_tensor(barcode_image)
            
            return (tensor_image,)
            
        except Exception as e:
            raise RuntimeError(f"Barcode generation failed: {str(e)}")

    def _create_barcode(self, data, barcode_type, fontsize, textdistance):
        """Create barcode using the barcode library."""
        code_class = barcode.get_barcode_class(barcode_type)
        writer = ImageWriter()
        barcode_obj = code_class(data, writer)
        
        options = {
            "font_size": fontsize,
            "text_distance": textdistance
        }
        
        return barcode_obj.render(options)