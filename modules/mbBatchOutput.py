"""
Dynamic Batch Output Node for ComfyUI
Splits a batch of objects into multiple outputs for downstream processing.
Shows popup to configure number of outputs when first added.
"""

# Local imports
from .common import any_typ

# Configuration constants
MIN_OUTPUTS = 2
MAX_OUTPUTS = 16

class mbBatchOutput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "batch": (any_typ,),
                "outputs": ("INT", {
                    "default": -1,  # -1 indicates popup is needed
                    "min": MIN_OUTPUTS,
                    "max": MAX_OUTPUTS,
                    "step": 1
                })
            }
        }

    # Node metadata
    TITLE = "Dynamic Batch Output"
    RETURN_TYPES = tuple(any_typ for _ in range(MIN_OUTPUTS))
    RETURN_NAMES = tuple(f"output_{i+1}" for i in range(MIN_OUTPUTS))
    FUNCTION = "unbatch"
    CATEGORY = "unset"
    DESCRIPTION = "Split a batch of objects into multiple outputs. Configure number of outputs when added to workflow."

    def unbatch(self, batch, outputs, unique_id=None):
        # Unpack the tuple/list and pad with None if needed
        if not isinstance(batch, (tuple, list)):
            raise ValueError("Input must be a tuple or list")
        
        # Convert batch to list for easier manipulation
        batch_list = list(batch)
        
        # Create result list with actual outputs
        result = []
        for i in range(outputs if outputs > 0 else 0):
            if i < len(batch_list):
                result.append(batch_list[i])
            else:
                result.append(None)
        
        # Pad to MAX_OUTPUTS with None for unused outputs
        while len(result) < MAX_OUTPUTS:
            result.append(None)
        
        return tuple(result)