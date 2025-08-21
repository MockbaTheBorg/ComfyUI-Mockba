"""
Dynamic Batch Input Node for ComfyUI
Combines multiple inputs into a single batch for processing.
Shows popup to configure number of inputs when first added.
"""

# Local imports
from .common import any_typ

# Configuration constants
MIN_INPUTS = 2
MAX_INPUTS = 16

class mbBatchInput:
    def __init__(self):
        """Initialize the batch input node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "inputs": ("INT", {
                    "default": -1,  # -1 indicates popup is needed
                    "min": MIN_INPUTS,
                    "max": MAX_INPUTS,
                    "step": 1
                })
            }
        }

    # Node metadata
    TITLE = "Dynamic Batch Input"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("batch",)
    FUNCTION = "batch"
    CATEGORY = "unset"
    DESCRIPTION = "Combine multiple objects into a single batch. Configure number of inputs when added to workflow."

    def batch(self, inputs, unique_id=None, **kwargs):
        # Collect all the dynamic inputs
        valid_inputs = []
        for i in range(inputs if inputs > 0 else 0):
            key = f"input_{i+1}"
            if key in kwargs and kwargs[key] is not None:
                valid_inputs.append(kwargs[key])
        
        return (tuple(valid_inputs),)