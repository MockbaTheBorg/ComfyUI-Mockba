"""
Batch Input Node for ComfyUI
Combines multiple inputs into a single batch for processing.
"""

# Local imports
from .common import any_typ

NUM_CHANNELS = 4  # Change this to adjust number of inputs/outputs

class mbBatchInput:
    def __init__(self):
        """Initialize the batch input node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                f"input_{i+1}": (any_typ,) for i in range(NUM_CHANNELS)
            }
        }

    # Node metadata
    TITLE = "Batch Input"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("batch",)
    FUNCTION = "batch"
    CATEGORY = "unset"
    DESCRIPTION = "Combine multiple objects into a single batch for transfer over one wire."

    def batch(self, **kwargs):
        # Filter out None values and collect valid inputs into a tuple
        valid_inputs = []
        for i in range(NUM_CHANNELS):
            key = f"input_{i+1}"
            if key in kwargs and kwargs[key] is not None:
                valid_inputs.append(kwargs[key])
        
        return (tuple(valid_inputs),)