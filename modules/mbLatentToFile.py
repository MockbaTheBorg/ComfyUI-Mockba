"""
Latent to File Saver Node for ComfyUI
Saves latent tensors to files with support for single latents and batch processing.
"""

# Standard library imports
import os

# Third-party imports
import torch

# ComfyUI imports
import folder_paths

# Local imports
from .common import CATEGORIES


class mbLatentToFile:
    """Save latent tensors to files with automatic handling and batch support."""
    
    # Class constants
    DEFAULT_FILENAME = "latent"
    DEFAULT_EXTENSION = ".pt"
    
    def __init__(self):
        """Initialize the latent to file saver node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for latent file saving."""
        return {
            "required": {
                "latent": ("LATENT", {
                    "tooltip": "Input latent to save"
                }),
                "filename": ("STRING", {
                    "default": cls.DEFAULT_FILENAME,
                    "tooltip": "Base filename for saved latent(s) (extension optional)"
                }),
                "save_mode": (["single", "batch"], {
                    "default": "single",
                    "tooltip": "Single: save as one file, Batch: save each latent separately with numbers"
                }),
            }
        }

    # Node metadata
    RETURN_TYPES = ("LATENT", "INT")
    RETURN_NAMES = ("latent", "count")
    FUNCTION = "save_latent_to_file"
    CATEGORY = CATEGORIES["FILE_OPS"]
    DESCRIPTION = "Save latent tensors to files with support for single latents and batch processing of multiple latents."

    def save_latent_to_file(self, latent, filename, save_mode):
        """
        Save latent(s) to file(s).
        
        Args:
            latent: Input latent dict with "samples" tensor
            filename: Base filename for saved latent(s)
            save_mode: "single" for one file, "batch" for numbered files
            
        Returns:
            tuple: (original_latent, count_of_saved_latents)
        """
        try:
            # Prepare output directory
            output_dir = self._prepare_output_directory()
            
            # Get the latent tensor
            latent_tensor = latent["samples"]
            
            # Save latents based on mode
            if save_mode == "single" or latent_tensor.shape[0] == 1:
                count = self._save_single_latent(latent, filename, output_dir)
            else:  # batch mode
                count = self._save_batch_latents(latent, filename, output_dir)
            
            return (latent, count)
            
        except Exception as e:
            error_msg = f"Failed to save latent to file: {str(e)}"
            print(error_msg)
            return (latent, 0)

    def _prepare_output_directory(self):
        """Prepare output directory for saving latents."""
        output_dir = folder_paths.get_input_directory().replace("\\", "/") + "/"
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def _save_single_latent(self, latent, base_filename, output_dir):
        """Save a single latent (or entire batch as one file)."""
        # Generate filename
        filename = self._generate_filename(base_filename)
        filepath = output_dir + filename
        
        # Save latent
        try:
            torch.save(latent, filepath)
            print(f"Latent saved: {filepath}")
            return 1
        except Exception as e:
            print(f"Error saving latent {filename}: {str(e)}")
            return 0

    def _save_batch_latents(self, latent, base_filename, output_dir):
        """Save multiple latents from batch with numbered filenames."""
        latent_tensor = latent["samples"]
        count = 0
        
        for i in range(latent_tensor.shape[0]):
            # Extract single latent from batch
            single_latent_tensor = latent_tensor[i:i+1]  # Keep batch dimension
            single_latent = {"samples": single_latent_tensor}
            
            # Generate numbered filename
            numbered_filename = self._generate_filename(f"{base_filename}_{i}")
            filepath = output_dir + numbered_filename
            
            # Save latent
            try:
                torch.save(single_latent, filepath)
                print(f"Latent saved: {filepath}")
                count += 1
            except Exception as e:
                print(f"Error saving latent {numbered_filename}: {str(e)}")
                break
        
        return count

    def _generate_filename(self, base_filename):
        """Generate final filename with proper extension."""
        # Remove existing .pt or .pth extension if present
        extensions_to_remove = [".pt", ".pth", ".latent"]
        for ext in extensions_to_remove:
            if base_filename.lower().endswith(ext):
                base_filename = base_filename[:-len(ext)]
                break
        
        return base_filename + self.DEFAULT_EXTENSION
