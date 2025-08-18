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
    DEFAULT_FOREGROUND_COLOR = "#000000"
    DEFAULT_BACKGROUND_COLOR = "#FFFFFF"
    
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
                "foreground_color": ("STRING", {
                    "default": cls.DEFAULT_FOREGROUND_COLOR,
                    "tooltip": "Foreground color in hex format (e.g., #000000)"
                }),
                "background_color": ("STRING", {
                    "default": cls.DEFAULT_BACKGROUND_COLOR,
                    "tooltip": "Background color in hex format (e.g., #FFFFFF)"
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
    TITLE = "Barcode Generator"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_barcode"
    CATEGORY = "unset"
    DESCRIPTION = "Generate barcode images from text with customizable formatting options."

    def generate_barcode(self, data, type, fontsize, textdistance, foreground_color, background_color, pdf417_columns=3, pdf417_security_level=2, pdf417_scale=3):
        """
        Generate a barcode image from input data.
        
        Args:
            data: Text to encode
            type: Barcode format
            fontsize: Font size for text (1D barcodes only)
            textdistance: Space between barcode and text (1D barcodes only)
            foreground_color: Foreground color in hex format
            background_color: Background color in hex format
            pdf417_columns: Number of columns for PDF417
            pdf417_security_level: Error correction level for PDF417
            pdf417_scale: Scale factor for PDF417
            
        Returns:
            tuple: Generated barcode image as tensor
        """
        try:
            # Generate barcode
            if type == "pdf417":
                barcode_image = self._create_pdf417(data, pdf417_columns, pdf417_security_level, pdf417_scale, foreground_color, background_color)
            else:
                barcode_image = self._create_barcode(data, type, fontsize, textdistance, foreground_color, background_color)
            
            # Convert to ComfyUI tensor format
            tensor_image = convert_pil_to_tensor(barcode_image)
            
            return (tensor_image,)
            
        except Exception as e:
            raise RuntimeError(f"Barcode generation failed: {str(e)}")

    def _create_barcode(self, data, barcode_type, fontsize, textdistance, foreground_color, background_color):
        """Create barcode using the barcode library."""
        code_class = barcode.get_barcode_class(barcode_type)
        writer = ImageWriter()
        barcode_obj = code_class(data, writer)
        
        options = {
            "font_size": fontsize,
            "text_distance": textdistance
        }
        
        # Generate the barcode
        barcode_image = barcode_obj.render(options)
        
        # Handle transparency and custom colors
        return self._apply_colors(barcode_image, foreground_color, background_color)

    def _create_pdf417(self, data, columns, security_level, scale, foreground_color, background_color):
        """Create PDF417 barcode using the pdf417gen library."""
        # Encode the data
        codes = pdf417gen.encode(
            data, 
            columns=columns, 
            security_level=security_level
        )
        
        # Render as image with custom colors
        pdf417_image = pdf417gen.render_image(
            codes,
            scale=scale,
            ratio=3,
            padding=20,
            fg_color=foreground_color,
            bg_color=background_color
        )
        
        return pdf417_image

    def _apply_colors(self, image, foreground_color, background_color):
        """Apply custom colors to a barcode image."""
        # Apply color mapping
        if image.mode == '1':  # 1-bit black and white
            image = image.convert('RGB')
        
        # Create a new image with custom colors
        pixels = image.load()
        width, height = image.size
        
        for y in range(height):
            for x in range(width):
                pixel = pixels[x, y]
                # Check if pixel is black (barcode) or white (background)
                if isinstance(pixel, tuple):
                    # RGB mode
                    if sum(pixel[:3]) < 384:  # Dark pixel (black-ish)
                        pixels[x, y] = tuple(int(foreground_color[i:i+2], 16) for i in (1, 3, 5))
                    else:  # Light pixel (white-ish)
                        pixels[x, y] = tuple(int(background_color[i:i+2], 16) for i in (1, 3, 5))
                else:
                    # Grayscale or 1-bit mode
                    if pixel < 128:  # Dark pixel
                        pixels[x, y] = tuple(int(foreground_color[i:i+2], 16) for i in (1, 3, 5))
                    else:  # Light pixel
                        pixels[x, y] = tuple(int(background_color[i:i+2], 16) for i in (1, 3, 5))
        
        return image