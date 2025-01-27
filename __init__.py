from .modules.mockba import *

# Maps node class names to their corresponding class.
NODE_CLASS_MAPPINGS = {
    "mb Image Batch": mbImageBatch,
    "mb Image Flip": mbImageFlip,
    "mb Image Rotate": mbImageRot,
    "mb Image Subtract": mbImageSubtract,
    "mb Image Dither": mbImageDither,
    "mb Image Dimensions": mbImageDimensions,
    "mb Image Load": mbImageLoad,
    "mb Image Load from URL": mbImageLoadURL,
    "mb Preview Bridge": mbPreviewBridge,
    "mb Image to File": mbImageToFile,
    "mb File to Image": mbFileToImage,
    "mb Text to File": mbTextToFile,
    "mb File to Text": mbFileToText,
    "mb Text or File": mbTextOrFile,
    "mb Debug": mbDebug,
    "mb Select": mbSelect,
    "mb Eval": mbEval,
    "mb Exec": mbExec,
    "mb Empty Latent Image": mbEmptyLatentImage,
    "mb KSampler": mbKSampler,
    "mb KSampler Advanced": mbKSamplerAdvanced,
    "mb Hash Generator": mbHashGenerator,
    "mb Text": mbText,
    "mb String": msString,
}


# Maps node class names to their corresponding display names.
NODE_DISPLAY_NAME_MAPPINGS = {
    "mb Image Batch": "Image Batch",
    "mb Image Flip": "Image Flip",
    "mb Image Rotate": "Image Rotate",
    "mb Image Subtract": "Image Subtract",
    "mb Image Dither": "Image Dither",
    "mb Image Dimensions": "Image Dimensions",
    "mb Image Load": "Image Load",
    "mb Image Load from URL": "Image Load from URL",
    "mb Preview Bridge": "Preview Bridge",
    "mb Image to File": "Image to File",
    "mb File to Image": "File to Image",
    "mb Text to File": "Text to File",
    "mb File to Text": "File to Text",
    "mb Text or File": "Text or File",
    "mb Debug": "Debug",
    "mb Select": "Select",
    "mb Eval": "Eval",
    "mb Exec": "Exec",
    "mb Empty Latent Image": "Empty Latent Image (gpu)",
    "mb KSampler": "KSampler (gpu)",
    "mb KSampler Advanced": "KSampler Advanced (gpu)",
    "mb Hash Generator": "Hash Generator",
    "mb Text": "Text",
    "mb String": "String",
}

WEB_DIRECTORY = "js"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
