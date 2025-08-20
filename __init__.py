import importlib
from .modules.common import CATEGORIES

# Initialize the mappings
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

def import_and_register(module_path, category=None):
    """
    Import a module, optionally set its category, and automatically register it in the mappings.
    
    Args:
        module_path: The module path (e.g., '.modules.mbTextbox')
        category: Optional category to override the class's default category
    
    Returns:
        The imported class
    """
    # Extract class name from module path (e.g., '.modules.mbTextbox' -> 'mbTextbox')
    class_name = module_path.split('.')[-1]
    
    # Import the module and get the class using importlib for relative imports
    module = importlib.import_module(module_path, package=__name__)
    cls = getattr(module, class_name)
    
    # Set category if provided
    if category is not None:
        cls.CATEGORY = category
    
    # Add to NODE_CLASS_MAPPINGS using class name as key
    NODE_CLASS_MAPPINGS[class_name] = cls
    
    # Add to NODE_DISPLAY_NAME_MAPPINGS using class TITLE
    if hasattr(cls, 'TITLE'):
        NODE_DISPLAY_NAME_MAPPINGS[class_name] = cls.TITLE
    else:
        # Fallback to class name if TITLE is not defined
        NODE_DISPLAY_NAME_MAPPINGS[class_name] = class_name
    
    return cls

# Import and register all modules
# === Data Management ===
category = CATEGORIES["DATA_MANAGEMENT"]
mbDataTypeConverter = import_and_register('.modules.mbDataTypeConverter', category)
mbDemux = import_and_register('.modules.mbDemux', category)
mbDeviceTransfer = import_and_register('.modules.mbDeviceTransfer', category)
mbHashGenerator = import_and_register('.modules.mbHashGenerator', category)
mbSelect = import_and_register('.modules.mbSelect', category)
mbSignal = import_and_register('.modules.mbSignal', category)
mbTensorChannel3to4 = import_and_register('.modules.mbTensorChannel3to4', category)
mbTensorChannel4to3 = import_and_register('.modules.mbTensorChannel4to3', category)
mbWirelessInput = import_and_register('.modules.mbWirelessInput', category)
mbWirelessOutput = import_and_register('.modules.mbWirelessOutput', category)

# === Development & Debugging ===
category = CATEGORIES["DEVELOPMENT"]
mbAIBypass = import_and_register('.modules.mbAIBypass', category)
mbAIDetector = import_and_register('.modules.mbAIDetector', category)
mbIlluminarty = import_and_register('.modules.mbIlluminarty', category)
mbColorPicker = import_and_register('.modules.mbColorPicker', category)
mbDebug = import_and_register('.modules.mbDebug', category)
mbDisplay = import_and_register('.modules.mbDisplay', category)
mbEval = import_and_register('.modules.mbEval', category)
mbExec = import_and_register('.modules.mbExec', category)
mbMemoryUnload = import_and_register('.modules.mbMemoryUnload', category)
mbSubmit = import_and_register('.modules.mbSubmit', category)
mbValue = import_and_register('.modules.mbValue', category)

# === File Operations ===
category = CATEGORIES["FILE_OPS"]
mbFileToImage = import_and_register('.modules.mbFileToImage', category)
mbFileToLatent = import_and_register('.modules.mbFileToLatent', category)
mbFileToText = import_and_register('.modules.mbFileToText', category)
mbImageLoad = import_and_register('.modules.mbImageLoad', category)
mbImageLoadURL = import_and_register('.modules.mbImageLoadURL', category)
mbImageToFile = import_and_register('.modules.mbImageToFile', category)
mbLatentToFile = import_and_register('.modules.mbLatentToFile', category)
mbTextOrFile = import_and_register('.modules.mbTextOrFile', category)
mbTextToFile = import_and_register('.modules.mbTextToFile', category)

# === Generation & Sampling ===
category = CATEGORIES["GENERATION"]
mbBarcode = import_and_register('.modules.mbBarcode', category)
mbEmptyLatentImage = import_and_register('.modules.mbEmptyLatentImage', category)
mbKSampler = import_and_register('.modules.mbKSampler', category)
mbQRCode = import_and_register('.modules.mbQRCode', category)

# === Image Processing ===
category = CATEGORIES["IMAGE_PROCESSING"]
mbImageBatch = import_and_register('.modules.mbImageBatch', category)
mbImageCenterRotate = import_and_register('.modules.mbImageCenterRotate', category)
mbImageDither = import_and_register('.modules.mbImageDither', category)
mbImageFFT = import_and_register('.modules.mbImageFFT', category)
mbImageFilmEffect = import_and_register('.modules.mbImageFilmEffect', category)
mbImageFlip = import_and_register('.modules.mbImageFlip', category)
mbImagePreview = import_and_register('.modules.mbImagePreview', category)
mbImageRotate = import_and_register('.modules.mbImageRotate', category)
mbImageSize = import_and_register('.modules.mbImageSize', category)
mbImageSubtract = import_and_register('.modules.mbImageSubtract', category)

# === Mask Processing ===
category = CATEGORIES["MASK_PROCESSING"]
mbMaskApply = import_and_register('.modules.mbMaskApply', category)
mbMaskFromColor = import_and_register('.modules.mbMaskFromColor', category)
mbMaskInvertIfEmpty = import_and_register('.modules.mbMaskInvertIfEmpty', category)

# === Text Processing ===
category = CATEGORIES["TEXT_PROCESSING"]
mbCLIPTextEncode = import_and_register('.modules.mbCLIPTextEncode', category)
mbString = import_and_register('.modules.mbString', category)
mbText = import_and_register('.modules.mbText', category)
mbTextbox = import_and_register('.modules.mbTextbox', category)

# Web directory for static files
WEB_DIRECTORY = "js"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]