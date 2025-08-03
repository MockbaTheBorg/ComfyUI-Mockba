from .modules.mbImageBatch import mbImageBatch
from .modules.mbImageFlip import mbImageFlip
from .modules.mbImageRotate import mbImageRotate
from .modules.mbImageSubtract import mbImageSubtract
from .modules.mbImageDither import mbImageDither
from .modules.mbImageDimensions import mbImageDimensions
from .modules.mbImageSize import mbImageSize
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
from .modules.mbDeviceTransfer import mbDeviceTransfer

# Maps node class names to their corresponding class.
NODE_CLASS_MAPPINGS = {
    "mb Image Batch": mbImageBatch,
    "mb Image Flip": mbImageFlip,
    "mb Image Rotate": mbImageRotate,
    "mb Image Subtract": mbImageSubtract,
    "mb Image Dither": mbImageDither,
    "mb Image Dimensions": mbImageDimensions,
    "mb Image Size": mbImageSize,
    "mb Image Load": mbImageLoad,
    "mb Image Load from URL": mbImageLoadURL,
    "mb Image Preview": mbImagePreview,
    "mb Image to File": mbImageToFile,
    "mb File to Image": mbFileToImage,
    "mb Text to File": mbTextToFile,
    "mb File to Text": mbFileToText,
    "mb Text or File": mbTextOrFile,
    "mb Debug": mbDebug,
    "mb Barcode": mbBarcode,
    "mb Select": mbSelect,
    "mb Eval": mbEval,
    "mb Exec": mbExec,
    "mb Demux": mbDemux,
    "mb Empty Latent Image": mbEmptyLatentImage,
    "mb KSampler": mbKSampler,
    "mb CLIP Text Encoder": mbCLIPTextEncode,
    "mb Hash Generator": mbHashGenerator,
    "mb Text": mbText,
    "mb Textbox": mbTextbox,
    "mb String": mbString,
    "mb Submit": mbSubmit,
    "mb Display": mbDisplay,
    "mb Device Transfer": mbDeviceTransfer,
}


# Maps node class names to their corresponding display names.
NODE_DISPLAY_NAME_MAPPINGS = {
    "mb Image Batch": "Image Batch",
    "mb Image Flip": "Image Flip",
    "mb Image Rotate": "Image Rotate",
    "mb Image Subtract": "Image Subtract",
    "mb Image Dither": "Image Dither",
    "mb Image Dimensions": "Image Dimensions",
    "mb Image Size": "Image Size",
    "mb Image Load": "Image Load",
    "mb Image Load from URL": "Image Load from URL",
    "mb Image Preview": "Image Preview",
    "mb Image to File": "Image to File",
    "mb File to Image": "File to Image",
    "mb Text to File": "Text to File",
    "mb File to Text": "File to Text",
    "mb Text or File": "Text or File",
    "mb Debug": "Debug",
    "mb Barcode": "Barcode",
    "mb Select": "Select",
    "mb Eval": "Eval",
    "mb Exec": "Exec",
    "mb Demux": "Demux",
    "mb Empty Latent Image": "Empty Latent Image (gpu)",
    "mb KSampler": "KSampler (gpu)",
    "mb CLIP Text Encoder": "CLIP Text Encoder",
    "mb Hash Generator": "Hash Generator",
    "mb Text": "Text",
    "mb Textbox": "Textbox",
    "mb String": "String",
    "mb Submit": "Submit",
    "mb Display": "Display",
    "mb Device Transfer": "Device Transfer",
}

WEB_DIRECTORY = "js"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
