"""
Barcode Generation Node for ComfyUI
Generates various barcode formats from text input with customizable styling.
"""

# Third-party imports
import barcode
from barcode.writer import ImageWriter
import pdf417gen

# Local imports
from .common import CATEGORIES, convert_pil_to_tensor


class mbBarcode:
    """Generate barcode images from text data with various format options."""
    
    # Class constants
    DEFAULT_DATA = "123456789"
    DEFAULT_TYPE = "code128"
    DEFAULT_FONT_SIZE = 10
    DEFAULT_TEXT_DISTANCE = 4
    
    # Combined barcode types (1D and 2D)
    BARCODE_TYPES = list(barcode.PROVIDED_BARCODES) + ["pdf417"]
    
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
                "type": (cls.BARCODE_TYPES, {
                    "default": cls.DEFAULT_TYPE,
                    "tooltip": "Barcode format type"
                }),
                "fontsize": ("INT", {
                    "default": cls.DEFAULT_FONT_SIZE,
                    **cls.FONT_SIZE_RANGE,
                    "tooltip": "Font size for barcode text (1D barcodes only)"
                }),
                "textdistance": ("INT", {
                    "default": cls.DEFAULT_TEXT_DISTANCE,
                    **cls.TEXT_DISTANCE_RANGE,
                    "tooltip": "Distance between barcode and text (1D barcodes only)"
                }),
            },
            "optional": {
                "pdf417_columns": ("INT", {
                    "default": 3,
                    "min": 1,
                    "max": 30,
                    "tooltip": "Number of columns for PDF417 (1-30, lower values for more data)"
                }),
                "pdf417_security_level": ("INT", {
                    "default": 2,
                    "min": 0,
                    "max": 8,
                    "tooltip": "Error correction level for PDF417 (0-8)"
                }),
                "pdf417_scale": ("INT", {
                    "default": 3,
                    "min": 1,
                    "max": 10,
                    "tooltip": "Scale factor for PDF417"
                }),
            }
        }

    # Node metadata
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_barcode"
    CATEGORY = CATEGORIES["GENERATION"]
    DESCRIPTION = "Generate barcode images from text with customizable formatting options."

    def generate_barcode(self, data, type, fontsize, textdistance, pdf417_columns=3, pdf417_security_level=2, pdf417_scale=3):
        """
        Generate a barcode image from input data.
        
        Args:
            data: Text to encode
            type: Barcode format
            fontsize: Font size for text (1D barcodes only)
            textdistance: Space between barcode and text (1D barcodes only)
            pdf417_columns: Number of columns for PDF417
            pdf417_security_level: Error correction level for PDF417
            pdf417_scale: Scale factor for PDF417
            
        Returns:
            tuple: Generated barcode image as tensor
        """
        try:
            # Generate barcode
            if type == "pdf417":
                barcode_image = self._create_pdf417(data, pdf417_columns, pdf417_security_level, pdf417_scale)
            else:
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

    def _create_pdf417(self, data, columns, security_level, scale):
        """Create PDF417 barcode using the pdf417gen library."""
        # Encode the data
        codes = pdf417gen.encode(
            data, 
            columns=columns, 
            security_level=security_level
        )
        
        # Render as image
        return pdf417gen.render_image(
            codes,
            scale=scale,
            ratio=3,
            padding=20,
            fg_color='#000',
            bg_color='#FFF'
        )