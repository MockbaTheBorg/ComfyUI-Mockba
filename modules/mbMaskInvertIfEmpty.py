"""
Mask Invert If Empty Node for ComfyUI
Inverts a mask if it's all zeros (empty), otherwise leaves it unchanged.
"""

# Standard library imports
import torch

# Local imports
from .common import CATEGORIES


class mbMaskInvertIfEmpty:
    """Invert mask if it's all zeros (empty), otherwise leave unchanged."""
    
    def __init__(self):
        """Initialize the mask invert if empty node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for mask processing."""
        return {
            "required": {
                "mask": ("MASK", {
                    "tooltip": "Input mask to check and potentially invert"
                }),
            }
        }

    # Node metadata
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)
    FUNCTION = "process_mask"
    CATEGORY = CATEGORIES["IMAGE_PROCESSING"]
    DESCRIPTION = "Inverts a mask if it's all zeros (empty), otherwise leaves it unchanged. Useful for ensuring masks have content."

    def process_mask(self, mask):
        """
        Process mask - invert if empty, otherwise leave unchanged.
        
        Args:
            mask: Input mask tensor in ComfyUI format [batch, height, width]
            
        Returns:
            tuple: Processed mask tensor
        """
        try:
            # Check if the mask is all zeros (empty)
            processed_mask = self._invert_if_empty(mask)
            
            return (processed_mask,)
            
        except Exception as e:
            error_msg = f"Failed to process mask: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)

    def _invert_if_empty(self, mask):
        """
        Invert mask if it's all zeros, otherwise return unchanged.
        
        Args:
            mask: Input mask tensor [batch, height, width]
            
        Returns:
            torch.Tensor: Processed mask tensor
        """
        # Check each mask in the batch
        batch_size = mask.shape[0]
        processed_masks = []
        
        for i in range(batch_size):
            current_mask = mask[i]
            
            # Check if the mask is all zeros (within a small tolerance for floating point)
            is_all_zeros = torch.all(current_mask < 1e-6)
            
            if is_all_zeros:
                # Invert: all zeros become all ones
                inverted_mask = torch.ones_like(current_mask)
                processed_masks.append(inverted_mask)
            else:
                # Keep original mask unchanged
                processed_masks.append(current_mask)
        
        # Stack all processed masks back into batch format
        result = torch.stack(processed_masks, dim=0)
        
        return result
