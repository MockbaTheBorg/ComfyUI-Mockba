from .modules.mbImageBatch import mbImageBatch
from .modules.mbImageFlip import mbImageFlip
from .modules.mbImageRotate import mbImageRotate
from .modules.mbImageCenterRotate import mbImageCenterRotate
from .modules.mbImageSubtract import mbImageSubtract
from .modules.mbImageDither import mbImageDither
from .modules.mbImageDimensions import mbImageDimensions
from .modules.mbImageSize import mbImageSize
from .modules.mbColorMask import mbColorMask
from .modules.mbColorPicker import mbColorPicker
from .modules.mbImageLoad import mbImageLoad
from .modules.mbImageLoadURL import mbImageLoadURL
from .modules.mbImagePreview import mbImagePreview
from .modules.mbImageToFile import mbImageToFile
from .modules.mbFileToImage import mbFileToImage
from .modules.mbTextToFile import mbTextToFile
from .modules.mbFileToText import mbFileToText
from .modules.mbTextOrFile import mbTextOrFile
from .modules.mbDebug import mbDebug
from .modules.mbBarcode import mbBarcode
from .modules.mbQRCode import mbQRCode
from .modules.mbSelect import mbSelect
from .modules.mbEval import mbEval
from .modules.mbExec import mbExec
from .modules.mbDemux import mbDemux
from .modules.mbEmptyLatentImage import mbEmptyLatentImage
from .modules.mbKSampler import mbKSampler
from .modules.mbCLIPTextEncode import mbCLIPTextEncode
from .modules.mbHashGenerator import mbHashGenerator
from .modules.mbText import mbText
from .modules.mbTextbox import mbTextbox
from .modules.mbString import mbString
from .modules.mbSubmit import mbSubmit
from .modules.mbDisplay import mbDisplay
from .modules.mbValue import mbValue
from .modules.mbDeviceTransfer import mbDeviceTransfer
from .modules.mbDataTypeConverter import mbDataTypeConverter
from .modules.mbTensorChannel4to3 import mbTensorChannel4to3
from .modules.mbMaskInvertIfEmpty import mbMaskInvertIfEmpty

# Maps node class names to their corresponding class.
NODE_CLASS_MAPPINGS = {
    # === Image Processing ===
    "mb Image Batch": mbImageBatch,
    "mb Image Flip": mbImageFlip,
    "mb Image Rotate": mbImageRotate,
    "mb Image Center Rotate": mbImageCenterRotate,
    "mb Image Subtract": mbImageSubtract,
    "mb Image Dither": mbImageDither,
    "mb Image Dimensions": mbImageDimensions,
    "mb Image Size": mbImageSize,
    "mb Color Mask": mbColorMask,
    "mb Color Picker": mbColorPicker,
    "mb Mask Invert If Empty": mbMaskInvertIfEmpty,
    "mb Image Preview": mbImagePreview,
    
    # === File Operations ===
    "mb Image Load": mbImageLoad,
    "mb Image Load from URL": mbImageLoadURL,
    "mb Image to File": mbImageToFile,
    "mb File to Image": mbFileToImage,
    "mb Text to File": mbTextToFile,
    "mb File to Text": mbFileToText,
    "mb Text or File": mbTextOrFile,
    
    # === Text Processing ===
    "mb Text": mbText,
    "mb Textbox": mbTextbox,
    "mb String": mbString,
    "mb CLIP Text Encoder": mbCLIPTextEncode,
    
    # === Generation & Sampling ===
    "mb Empty Latent Image": mbEmptyLatentImage,
    "mb KSampler": mbKSampler,
    "mb Barcode": mbBarcode,
    "mb QR Code": mbQRCode,
    
    # === Data Management ===
    "mb Select": mbSelect,
    "mb Demux": mbDemux,
    "mb Device Transfer": mbDeviceTransfer,
    "mb Data Type Converter": mbDataTypeConverter,
    "mb Tensor Channel 4 to 3": mbTensorChannel4to3,
    "mb Hash Generator": mbHashGenerator,
    
    # === Development & Debugging ===
    "mb Debug": mbDebug,
    "mb Display": mbDisplay,
    "mb Value": mbValue,
    "mb Submit": mbSubmit,
    "mb Eval": mbEval,
    "mb Exec": mbExec,
}


# Maps node class names to their corresponding display names.
NODE_DISPLAY_NAME_MAPPINGS = {
    # === Image Processing ===
    "mb Image Batch": "Image Batch",
    "mb Image Flip": "Image Flip",
    "mb Image Rotate": "Image Rotate",
    "mb Image Center Rotate": "Image Center Rotate",
    "mb Image Subtract": "Image Subtract",
    "mb Image Dither": "Image Dither",
    "mb Image Dimensions": "Image Dimensions",
    "mb Image Size": "Image Size",
    "mb Color Mask": "Color Mask",
    "mb Color Picker": "Color Picker",
    "mb Mask Invert If Empty": "Mask Invert If Empty",
    "mb Image Preview": "Image Preview",
    
    # === File Operations ===
    "mb Image Load": "Image Load",
    "mb Image Load from URL": "Image Load from URL",
    "mb Image to File": "Image to File",
    "mb File to Image": "File to Image",
    "mb Text to File": "Text to File",
    "mb File to Text": "File to Text",
    "mb Text or File": "Text or File",
    
    # === Text Processing ===
    "mb Text": "Text",
    "mb Textbox": "Textbox",
    "mb String": "String",
    "mb CLIP Text Encoder": "CLIP Text Encoder",
    
    # === Generation & Sampling ===
    "mb Empty Latent Image": "Empty Latent Image (gpu)",
    "mb KSampler": "KSampler (gpu)",
    "mb Barcode": "Barcode",
    "mb QR Code": "QR Code",
    
    # === Data Management ===
    "mb Select": "Select",
    "mb Demux": "Demux",
    "mb Device Transfer": "Device Transfer",
    "mb Data Type Converter": "Data Type Converter",
    "mb Tensor Channel 4 to 3": "Tensor Channel 4 to 3",
    "mb Hash Generator": "Hash Generator",
    
    # === Development & Debugging ===
    "mb Debug": "Debug",
    "mb Display": "Display",
    "mb Value": "Value",
    "mb Submit": "Submit",
    "mb Eval": "Eval",
    "mb Exec": "Exec",
}

WEB_DIRECTORY = "js"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
