"""
Latent Inspector Node for ComfyUI
Inspects and displays information about latent tensors.
"""

# Third-party imports
import torch

# Local imports
from .common import CATEGORIES

class mbLatentInspector:
    """Inspect latent tensors and display their properties."""

    def __init__(self):
        """Initialize the latent inspector node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for latent inspection."""
        return {
            "required": {
                "latent": ("LATENT", {"tooltip": "The latent tensor to inspect."}),
                "show_details": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Show detailed information about the latent tensor"
                })
            }
        }

    # Node metadata
    TITLE = "Latent Inspector"
    RETURN_TYPES = ("LATENT", "STRING")
    RETURN_NAMES = ("latent", "info")
    FUNCTION = "inspect_latent"
    CATEGORY = CATEGORIES["DEVELOPMENT"]
    DESCRIPTION = "Inspect latent tensors and display their shape, channels, and other properties."

    def inspect_latent(self, latent, show_details):
        """
        Inspect the latent tensor and return information about it.

        Args:
            latent: The latent tensor to inspect
            show_details: Whether to show detailed information

        Returns:
            tuple: (latent, info_string) - passes through latent and returns info
        """
        try:
            samples = latent["samples"]

            # Basic information
            shape = samples.shape
            channels = shape[1]
            batch_size = shape[0]
            height = shape[2]
            width = shape[3]

            # Determine latent type
            if channels == 4:
                latent_type = "Regular (SD1/SD2)"
            elif channels == 16:
                latent_type = "SD3"
            elif channels == 8:
                latent_type = "SDXL"
            else:
                latent_type = f"Unknown ({channels} channels)"

            # Create info string
            info = f"Latent Shape: {shape}\n"
            info += f"Type: {latent_type}\n"
            info += f"Batch Size: {batch_size}\n"
            info += f"Channels: {channels}\n"
            info += f"Height: {height}\n"
            info += f"Width: {width}\n"

            if show_details:
                info += f"Data Type: {samples.dtype}\n"
                info += f"Device: {samples.device}\n"
                info += f"Memory Usage: {samples.numel() * samples.element_size()} bytes\n"
                info += f"Min Value: {samples.min().item():.6f}\n"
                info += f"Max Value: {samples.max().item():.6f}\n"
                info += f"Mean Value: {samples.mean().item():.6f}\n"
                info += f"Std Deviation: {samples.std().item():.6f}\n"

            # Print to console as well
            print("=== Latent Inspector ===")
            print(info)
            print("=" * 30)

            return (latent, info)

        except Exception as e:
            error_info = f"Error inspecting latent: {str(e)}"
            print(error_info)
            return (latent, error_info)
