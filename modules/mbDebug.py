from pprint import pformat
import torch
from .common import *

# Shows debug information about the input object.
class mbDebug:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "input": (any_typ, {}),
                "debug_output": ("STRING", {"multiline": True, "default": "Debug output will appear here after execution..."}),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/utility"
    DESCRIPTION = "Shows debug information about the input object in a text widget."
    OUTPUT_NODE = True

    def execute(self, input, debug_output):
        debug_lines = []
        debug_lines.append("Debug Info:")
        debug_lines.append("-" * 40)
        
        # Check if input is a tensor
        if hasattr(input, 'shape') and hasattr(input, 'dtype'):
            debug_lines.append("TENSOR INFORMATION:")
            debug_lines.append(f"  Type: {type(input).__name__}")
            debug_lines.append(f"  Shape: {input.shape}")
            debug_lines.append(f"  Data type: {input.dtype}")
            debug_lines.append(f"  Device: {getattr(input, 'device', 'N/A')}")
            debug_lines.append(f"  Requires grad: {getattr(input, 'requires_grad', 'N/A')}")
            
            # Add min/max values if it's a numeric tensor
            try:
                if hasattr(input, 'min') and hasattr(input, 'max'):
                    debug_lines.append(f"  Min value: {input.min().item()}")
                    debug_lines.append(f"  Max value: {input.max().item()}")
                    debug_lines.append(f"  Mean value: {input.float().mean().item():.6f}")
            except:
                pass
                
            debug_lines.append("")
            
        elif isinstance(input, object) and not isinstance(
            input, (str, int, float, bool, list, dict, tuple)
        ):
            debug_lines.append("OBJECT INFORMATION:")
            debug_lines.append(f"  Type: {type(input).__name__}")
            debug_lines.append("  Available methods and attributes:")
            debug_lines.append(pformat(dir(input), indent=4))
        else:
            debug_lines.append("VALUE INFORMATION:")
            debug_lines.append(f"  Type: {type(input).__name__}")
            debug_lines.append(f"  Value: {str(input)}")

        # Join all debug output into a single string
        debug_text = "\n".join(debug_lines)
        
        return {"ui": {"debug_output": [debug_text]}}
