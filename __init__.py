from .modules.common import CATEGORIES

from .modules.mbAIBypass import mbAIBypass
from .modules.mbAIDetector import mbAIDetector
from .modules.mbIlluminarty import mbIlluminarty
from .modules.mbBarcode import mbBarcode
from .modules.mbCLIPTextEncode import mbCLIPTextEncode
from .modules.mbColorPicker import mbColorPicker
from .modules.mbDataTypeConverter import mbDataTypeConverter
from .modules.mbDebug import mbDebug
from .modules.mbDemux import mbDemux
from .modules.mbDeviceTransfer import mbDeviceTransfer
from .modules.mbDisplay import mbDisplay
from .modules.mbEmptyLatentImage import mbEmptyLatentImage
from .modules.mbEval import mbEval
from .modules.mbExec import mbExec
from .modules.mbFileToImage import mbFileToImage
from .modules.mbFileToLatent import mbFileToLatent
from .modules.mbFileToText import mbFileToText
from .modules.mbHashGenerator import mbHashGenerator
from .modules.mbImageBatch import mbImageBatch
from .modules.mbImageCenterRotate import mbImageCenterRotate
from .modules.mbImageDither import mbImageDither
from .modules.mbImageFilmEffect import mbImageFilmEffect
from .modules.mbImageFFT import mbImageFFT
from .modules.mbImageFlip import mbImageFlip
from .modules.mbImageLoad import mbImageLoad
from .modules.mbImageLoadURL import mbImageLoadURL
from .modules.mbImagePreview import mbImagePreview
from .modules.mbImageRotate import mbImageRotate
from .modules.mbImageSize import mbImageSize
from .modules.mbImageSubtract import mbImageSubtract
from .modules.mbImageToFile import mbImageToFile
from .modules.mbKSampler import mbKSampler
from .modules.mbLatentToFile import mbLatentToFile
from .modules.mbMaskApply import mbMaskApply
from .modules.mbMaskFromColor import mbMaskFromColor
from .modules.mbMemoryUnload import mbMemoryUnload
from .modules.mbMaskInvertIfEmpty import mbMaskInvertIfEmpty
from .modules.mbQRCode import mbQRCode
from .modules.mbSelect import mbSelect
from .modules.mbString import mbString
from .modules.mbSubmit import mbSubmit
from .modules.mbTensorChannel4to3 import mbTensorChannel4to3
from .modules.mbText import mbText
from .modules.mbTextbox import mbTextbox
from .modules.mbTextOrFile import mbTextOrFile
from .modules.mbTextToFile import mbTextToFile
from .modules.mbValue import mbValue

# Maps node class names to their corresponding class.
NODE_CLASS_MAPPINGS = {
    # === Data Management ===
    "mb Data Type Converter": mbDataTypeConverter,
    "mb Demux": mbDemux,
    "mb Device Transfer": mbDeviceTransfer,
    "mb Hash Generator": mbHashGenerator,
    "mb Select": mbSelect,
    "mb Tensor Channel 4 to 3": mbTensorChannel4to3,
    
    # === Development & Debugging ===
    "mb AI Bypass": mbAIBypass,
    "mb AI Detector": mbAIDetector,
    "mb Color Picker": mbColorPicker,
    "mb Debug": mbDebug,
    "mb Display": mbDisplay,
    "mb Eval": mbEval,
    "mb Exec": mbExec,
    "mb Memory Unload": mbMemoryUnload,
    "mb Submit": mbSubmit,
    "mb Value": mbValue,
    
    # === File Operations ===
    "mb File to Image": mbFileToImage,
    "mb File to Latent": mbFileToLatent,
    "mb File to Text": mbFileToText,
    "mb Image Load": mbImageLoad,
    "mb Image Load from URL": mbImageLoadURL,
    "mb Image to File": mbImageToFile,
    "mb Latent to File": mbLatentToFile,
    "mb Text or File": mbTextOrFile,
    "mb Text to File": mbTextToFile,
    
    # === Generation & Sampling ===
    "mb Barcode": mbBarcode,
    "mb Empty Latent Image": mbEmptyLatentImage,
    "mb KSampler": mbKSampler,
    "mb QR Code": mbQRCode,
    
    # === Image Processing ===
    "mb Illuminarty": mbIlluminarty,
    "mb Image Batch": mbImageBatch,
    "mb Image Center Rotate": mbImageCenterRotate,
    "mb Image Dither": mbImageDither,
    "mb Image FFT": mbImageFFT,
    "mb Image Film Effect": mbImageFilmEffect,
    "mb Image Flip": mbImageFlip,
    "mb Image Preview": mbImagePreview,
    "mb Image Rotate": mbImageRotate,
    "mb Image Size": mbImageSize,
    "mb Image Subtract": mbImageSubtract,
    
    # === Mask Processing ===
    "mb Mask Apply": mbMaskApply,
    "mb Mask from Color": mbMaskFromColor,
    "mb Mask Invert if Empty": mbMaskInvertIfEmpty,

    # === Text Processing ===
    "mb CLIP Text Encoder": mbCLIPTextEncode,
    "mb String": mbString,
    "mb Text": mbText,
    "mb Textbox": mbTextbox,
}


# Maps node class names to their corresponding display names.
NODE_DISPLAY_NAME_MAPPINGS = {
    # === Data Management ===
    "mb Data Type Converter": "Data Type Converter",
    "mb Demux": "Demux",
    "mb Device Transfer": "Device Transfer",
    "mb Hash Generator": "Hash Generator",
    "mb Select": "Select",
    "mb Tensor Channel 4 to 3": "Tensor Channel 4 to 3",
    
    # === Development & Debugging ===
    "mb AI Bypass": "AI Bypass",
    "mb AI Detector": "AI Detector",
    "mb Color Picker": "Color Picker",
    "mb Debug": "Debug",
    "mb Display": "Display",
    "mb Eval": "Eval",
    "mb Exec": "Exec",
    "mb Memory Unload": "Memory Unload",
    "mb Submit": "Submit",
    "mb Value": "Value",
    
    # === File Operations ===
    "mb File to Image": "File to Image",
    "mb File to Latent": "File to Latent",
    "mb File to Text": "File to Text",
    "mb Image Load": "Image Load",
    "mb Image Load from URL": "Image Load from URL",
    "mb Image to File": "Image to File",
    "mb Latent to File": "Latent to File",
    "mb Text or File": "Text or File",
    "mb Text to File": "Text to File",
    
    # === Generation & Sampling ===
    "mb Barcode": "Barcode",
    "mb Empty Latent Image": "Empty Latent Image (gpu)",
    "mb KSampler": "KSampler (gpu)",
    "mb QR Code": "QR Code",
    
    # === Image Processing ===
    "mb Illuminarty": "Illuminarty AI Detector",
    "mb Image Batch": "Image Batch",
    "mb Image Center Rotate": "Image Center Rotate",
    "mb Image Dither": "Image Dither",
    "mb Image FFT": "Image FFT",
    "mb Image Film Effect": "Image Film Effect",
    "mb Image Flip": "Image Flip",
    "mb Image Preview": "Image Preview",
    "mb Image Rotate": "Image Rotate",
    "mb Image Size": "Image Size",
    "mb Image Subtract": "Image Subtract",
    
    # === Mask Processing ===
    "mb Mask Apply": "Mask Apply",
    "mb Mask from Color": "Mask from Color",
    "mb Mask Invert if Empty": "Mask Invert if Empty",

    # === Text Processing ===
    "mb CLIP Text Encoder": "CLIP Text Encoder",
    "mb String": "String",
    "mb Text": "Text",
    "mb Textbox": "Textbox",
}

WEB_DIRECTORY = "js"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]