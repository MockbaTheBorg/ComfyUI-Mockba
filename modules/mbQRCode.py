"""
QR Code Generation Node for ComfyUI
Generates QR codes from text input with customizable styling and error correction.
"""

# Third-party imports
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

# Local imports
from .common import CATEGORIES, convert_pil_to_tensor


class mbQRCode:
    """Generate QR code images from text data with various customization options."""
    
    # Class constants
    DEFAULT_DATA = "Hello QR Code!"
    DEFAULT_VERSION = 1
    DEFAULT_ERROR_CORRECTION = "M"
    DEFAULT_BOX_SIZE = 10
    DEFAULT_BORDER = 4
    DEFAULT_FILL_COLOR = "#000000"
    DEFAULT_BACK_COLOR = "#FFFFFF"
    
    # Error correction mapping
    ERROR_CORRECTION_MAP = {
        "L": ERROR_CORRECT_L,  # ~7% correction
        "M": ERROR_CORRECT_M,  # ~15% correction
        "Q": ERROR_CORRECT_Q,  # ~25% correction
        "H": ERROR_CORRECT_H   # ~30% correction
    }
    
    # Input validation ranges
    VERSION_RANGE = {"min": 1, "max": 40}
    BOX_SIZE_RANGE = {"min": 1, "max": 50}
    BORDER_RANGE = {"min": 0, "max": 20}
    
    def __init__(self):
        """Initialize the QR code generator node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types and validation."""
        return {
            "required": {
                "data": ("STRING", {
                    "default": cls.DEFAULT_DATA,
                    "tooltip": "Text data to encode in QR code"
                }),
                "version": ("INT", {
                    "default": cls.DEFAULT_VERSION,
                    **cls.VERSION_RANGE,
                    "tooltip": "QR code version (1-40, higher = more data capacity)"
                }),
                "error_correction": (list(cls.ERROR_CORRECTION_MAP.keys()), {
                    "default": cls.DEFAULT_ERROR_CORRECTION,
                    "tooltip": "Error correction level (L=~7%, M=~15%, Q=~25%, H=~30%)"
                }),
                "box_size": ("INT", {
                    "default": cls.DEFAULT_BOX_SIZE,
                    **cls.BOX_SIZE_RANGE,
                    "tooltip": "Size of each box in pixels"
                }),
                "border": ("INT", {
                    "default": cls.DEFAULT_BORDER,
                    **cls.BORDER_RANGE,
                    "tooltip": "Border size in boxes"
                }),
                "foreground_color": ("STRING", {
                    "default": cls.DEFAULT_FILL_COLOR,
                    "tooltip": "Foreground color in hex format (e.g., #000000)"
                }),
                "background_color": ("STRING", {
                    "default": cls.DEFAULT_BACK_COLOR,
                    "tooltip": "Background color in hex format (e.g., #FFFFFF)"
                }),
            },
            "optional": {
            }
        }

    # Node metadata
    TITLE = "QR Code Generator"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_qrcode"
    CATEGORY = CATEGORIES["GENERATION"]
    DESCRIPTION = "Generate QR code images from text with customizable error correction and styling."

    def generate_qrcode(self, data, version, error_correction, box_size, border, foreground_color, background_color):
        """
        Generate a QR code image from input data.
        
        Args:
            data: Text to encode
            version: QR code version (1-40)
            error_correction: Error correction level (L/M/Q/H)
            box_size: Size of each box in pixels
            border: Border size in boxes
            foreground_color: Foreground color in hex format
            background_color: Background color in hex format
            
        Returns:
            tuple: Generated QR code image as tensor
        """
        try:
            # Generate QR code
            qr_image = self._create_qrcode(
                data, version, error_correction, box_size, border, 
                foreground_color, background_color
            )
            
            # Convert to ComfyUI tensor format
            tensor_image = convert_pil_to_tensor(qr_image)
            
            return (tensor_image,)
            
        except Exception as e:
            raise RuntimeError(f"QR code generation failed: {str(e)}")

    def _create_qrcode(self, data, version, error_correction, box_size, border, foreground_color, background_color):
        """Create QR code using the qrcode library."""
        # Create QR code instance
        qr = qrcode.QRCode(
            version=version,
            error_correction=self.ERROR_CORRECTION_MAP[error_correction],
            box_size=box_size,
            border=border,
        )
        
        # Add data and generate
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create with custom colors
        qr_image = qr.make_image(fill_color=foreground_color, back_color=background_color)
        
        # Convert from 1-bit mode to RGB mode for proper tensor conversion
        if qr_image.mode != 'RGB':
            qr_image = qr_image.convert('RGB')
        
        return qr_image
