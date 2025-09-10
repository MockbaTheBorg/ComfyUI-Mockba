"""
Delay Node for ComfyUI
Delays the passthrough of any input by a specified number of seconds.
"""

# Standard library imports
import time

# ComfyUI imports
import comfy.utils

# Local imports
from .common import any_typ

class mbDelay:
    """Delay node that pauses execution for a specified number of seconds before passing through the input."""
    
    # Class constants
    DEFAULT_SECONDS = 1.0
    MIN_SECONDS = 0.0
    MAX_SECONDS = 3600.0  # 1 hour maximum
    
    def __init__(self):
        """Initialize the delay node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for the delay node."""
        return {
            "required": {
                "input": (any_typ, {
                    "tooltip": "Any object to delay and pass through"
                }),
                "seconds": ("FLOAT", {
                    "default": cls.DEFAULT_SECONDS,
                    "min": cls.MIN_SECONDS,
                    "max": cls.MAX_SECONDS,
                    "step": 0.1,
                    "tooltip": "Number of seconds to delay before passing through the input"
                }),
            }
        }

    # Node metadata
    TITLE = "Delay"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("output",)
    FUNCTION = "delay_passthrough"
    CATEGORY = "unset"
    DESCRIPTION = "Delays the passthrough of any input by a specified number of seconds using a proper sleep function."

    def delay_passthrough(self, input, seconds):
        """
        Delay execution for the specified number of seconds, then return the input unchanged.
        
        Args:
            input: Any object to pass through after the delay
            seconds: Number of seconds to delay
            
        Returns:
            tuple: The input object unchanged
        """
        if seconds <= 0:
            return (input,)
        
        # Check if progress bar is enabled
        if not comfy.utils.PROGRESS_BAR_ENABLED:
            time.sleep(seconds)
            return (input,)
        
        # Create progress bar for the delay
        step_time = 0.1  # Update every 0.1 seconds
        total_steps = max(1, int(seconds / step_time))
        pbar = comfy.utils.ProgressBar(total_steps)
        
        remaining_time = seconds
        for step in range(total_steps):
            sleep_time = min(step_time, remaining_time)
            time.sleep(sleep_time)
            remaining_time -= sleep_time
            pbar.update_absolute(step + 1, total_steps)
        
        # Sleep any remaining fractional time
        if remaining_time > 0:
            time.sleep(remaining_time)
            pbar.update_absolute(total_steps, total_steps)
        
        # Return the input unchanged
        return (input,)