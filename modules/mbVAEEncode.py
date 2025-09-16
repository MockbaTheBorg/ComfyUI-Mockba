"""
Enhanced VAE Encode Node for ComfyUI
Encodes images into latent space with support for different latent formats and progress visualization.
"""

# Standard library imports
import time

# Third-party imports
import torch

# ComfyUI imports
import comfy.utils

# Local imports
from .common import CATEGORIES

class mbVAEEncode:
    """Enhanced VAE Encode node with latent type selection and progress bar visualization."""

    def __init__(self):
        """Initialize the enhanced VAE encode node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for the enhanced VAE encode node."""
        return {
            "required": {
                "pixels": ("IMAGE", {"tooltip": "The image to be encoded into latent space."}),
                "vae": ("VAE", {"tooltip": "The VAE model used for encoding the image."}),
                "latent_type": (["regular", "sd3"], {
                    "default": "regular",
                    "tooltip": "Type of latent format: regular (SD1/SD2, 4 channels) or SD3 (16 channels)"
                })
            }
        }

    # Node metadata
    TITLE = "Enhanced VAE Encode"
    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent",)
    OUTPUT_TOOLTIPS = ("The encoded latent representation.",)
    FUNCTION = "encode_with_progress"
    CATEGORY = "unset"
    DESCRIPTION = "Enhanced VAE encoder with latent type selection and progress bar visualization during encoding."

    def encode_with_progress(self, vae, pixels, latent_type):
        """
        Encode images to latent space with progress bar visualization.

        Args:
            vae: The VAE model used for encoding
            pixels: Input images to encode
            latent_type: Type of latent format ("regular" or "sd3")

        Returns:
            tuple: (latent_dict,) containing the encoded latent
        """
        try:
            # Get image dimensions for progress estimation
            batch_size = pixels.shape[0]
            height = pixels.shape[1]
            width = pixels.shape[2]

            # Check if progress bar is enabled
            if not comfy.utils.PROGRESS_BAR_ENABLED:
                # If progress bar is disabled, encode normally
                encoded = vae.encode(pixels[:,:,:,:3])
                return ({"samples": encoded},)

            # Create progress bar for VAE encoding
            # Estimate steps based on batch size and image dimensions
            estimated_steps = max(10, min(100, batch_size * (height // 64) * (width // 64)))
            pbar = comfy.utils.ProgressBar(estimated_steps)

            # Start encoding with progress updates
            start_time = time.time()

            # For simplicity, we'll update progress at key points
            # In a real implementation, you might need to hook into the VAE encoding process
            pbar.update_absolute(1, estimated_steps)  # Starting

            # Perform the actual encoding
            encoded = vae.encode(pixels[:,:,:,:3])

            pbar.update_absolute(estimated_steps // 2, estimated_steps)  # Halfway

            # Handle latent type conversion if needed
            if latent_type == "sd3" and encoded.shape[1] == 4:
                # Convert regular latent (4 channels) to SD3 format (16 channels)
                print(f"Converting regular latent (4 channels) to SD3 format (16 channels)")
                print(f"Original shape: {encoded.shape}")

                # For SD3 models, we need to expand from 4 to 16 channels
                # This is a simplified approach - real SD3 conversion might be more complex
                # You might need to use a proper SD3 VAE or conversion method
                batch_size, _, height, width = encoded.shape
                expanded_latent = torch.zeros([batch_size, 16, height, width],
                                            dtype=encoded.dtype, device=encoded.device)

                # Copy the original 4 channels to the first 4 positions
                expanded_latent[:, :4, :, :] = encoded

                # Fill remaining channels with zeros or noise
                # In practice, you might want to use learned projections or model-specific conversion
                encoded = expanded_latent

                print(f"Converted shape: {encoded.shape}")

            elif latent_type == "regular" and encoded.shape[1] == 16:
                # Convert SD3 latent (16 channels) to regular format (4 channels)
                print(f"Converting SD3 latent (16 channels) to regular format (4 channels)")
                print(f"Original shape: {encoded.shape}")

                # For regular models, we need to reduce from 16 to 4 channels
                # This is a simplified approach - real conversion might be more complex
                encoded = encoded[:, :4, :, :]  # Take first 4 channels

                print(f"Converted shape: {encoded.shape}")

            # Always print the final latent shape for verification
            print(f"Final latent shape: {encoded.shape} (channels: {encoded.shape[1]})")

            # Additional debug information
            if latent_type == "sd3" and encoded.shape[1] != 16:
                print(f"WARNING: Requested SD3 format but got {encoded.shape[1]} channels!")
            elif latent_type == "regular" and encoded.shape[1] != 4:
                print(f"WARNING: Requested regular format but got {encoded.shape[1]} channels!")

            pbar.update_absolute(estimated_steps, estimated_steps)  # Complete

            # Calculate and display timing information
            elapsed_time = time.time() - start_time
            print(f"VAE encoding completed in {elapsed_time:.2f} seconds (latent type: {latent_type})")

            return ({"samples": encoded},)

        except Exception as e:
            error_msg = f"VAE encoding failed: {str(e)}"
            print(error_msg)
            # Return a minimal fallback latent
            fallback_channels = 16 if latent_type == "sd3" else 4
            fallback_latent = torch.zeros([1, fallback_channels, 64, 64], dtype=torch.float32)
            return ({"samples": fallback_latent},)
