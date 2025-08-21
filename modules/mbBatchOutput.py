"""
Batch Output Node for ComfyUI
Splits a batch of objects into multiple outputs for downstream processing.
"""

# Local imports
from .common import any_typ

NUM_CHANNELS = 4  # Change this to adjust number of inputs/outputs

class mbBatchOutput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"batch": (any_typ,)}
        }

    # Node metadata
    TITLE = "Batch Output"
    RETURN_TYPES = tuple(any_typ for _ in range(NUM_CHANNELS))
    RETURN_NAMES = tuple(f"output_{i+1}" for i in range(NUM_CHANNELS))
    FUNCTION = "unbatch"
    CATEGORY = "unset"
    DESCRIPTION = "Split a batch of objects into multiple outputs for downstream processing."

    def unbatch(self, batch):
        # Unpack the tuple/list and pad with None if needed
        if not isinstance(batch, (tuple, list)):
            raise ValueError("Input must be a tuple or list")
        
        # Convert batch to list for easier manipulation
        batch_list = list(batch)
        
        # Pad with None if batch is shorter than NUM_CHANNELS
        while len(batch_list) < NUM_CHANNELS:
            batch_list.append(None)
        
        # Truncate if batch is longer than NUM_CHANNELS
        if len(batch_list) > NUM_CHANNELS:
            batch_list = batch_list[:NUM_CHANNELS]
        
        return tuple(batch_list)