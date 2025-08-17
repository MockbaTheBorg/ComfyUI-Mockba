"""
File to Latent Loader Node for ComfyUI
Loads latent tensors from files with support for single latents and batch loading.
"""

# Standard library imports
import os

# Third-party imports
import torch

# ComfyUI imports
import folder_paths

# Local imports
from .common import CATEGORIES


class mbFileToLatent:
    """Load latent tensors from files with automatic handling and batch support."""
    
    # Class constants
    DEFAULT_FILENAME = "latent"
    SUPPORTED_EXTENSIONS = [".pt", ".pth", ".latent"]
    DEFAULT_EXTENSION = ".pt"
    
    # Default latent dimensions for fallback (standard SD latent size)
    DEFAULT_BATCH = 1
    DEFAULT_CHANNELS = 4
    DEFAULT_HEIGHT = 64
    DEFAULT_WIDTH = 64
    
    def __init__(self):
        """Initialize the file to latent loader node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for latent file loading."""
        return {
            "required": {
                "filename": ("STRING", {
                    "default": cls.DEFAULT_FILENAME,
                    "tooltip": "Base filename for latent(s) to load (extension optional)"
                }),
                "load_mode": (["single", "batch"], {
                    "default": "single",
                    "tooltip": "Single: load one latent, Batch: load sequentially numbered latents"
                }),
            }
        }

    # Node metadata
    RETURN_TYPES = ("LATENT", "INT")
    RETURN_NAMES = ("latent", "count")
    FUNCTION = "load_latent_from_file"
    CATEGORY = CATEGORIES["FILE_OPS"]
    DESCRIPTION = "Load latent tensors from files with support for single latents and batch loading of sequentially numbered files. Returns default latent if file not found."

    def load_latent_from_file(self, filename, load_mode):
        """
        Load latent(s) from file(s).
        
        Args:
            filename: Base filename for latent(s) to load
            load_mode: "single" for one latent, "batch" for multiple numbered latents
            
        Returns:
            tuple: (latent_dict, count) where count is number of latents loaded
        """
        try:
            if load_mode == "single":
                latent_dict, count = self._load_single_latent(filename)
            else:  # batch mode
                latent_dict, count = self._load_batch_latents(filename)
            
            return (latent_dict, count)
            
        except Exception as e:
            error_msg = f"Failed to load latent from file: {str(e)}"
            print(error_msg)
            # Return default latent
            default_latent = self._create_default_latent()
            return (default_latent, 0)

    def _load_single_latent(self, base_filename):
        """Load a single latent file."""
        filepath = self._find_latent_file(base_filename)
        
        if filepath is None:
            error_msg = f"Latent file not found: {base_filename}"
            print(error_msg)
            default_latent = self._create_default_latent()
            return default_latent, 0
        
        try:
            latent_dict = self._load_and_process_latent(filepath)
            return latent_dict, 1
        except Exception as e:
            error_msg = f"Error loading latent {filepath}: {str(e)}"
            print(error_msg)
            default_latent = self._create_default_latent()
            return default_latent, 0

    def _load_batch_latents(self, base_filename):
        """Load multiple sequentially numbered latents."""
        latents = []
        i = 0
        
        while True:
            numbered_filename = f"{base_filename}_{i}"
            filepath = self._find_latent_file(numbered_filename)
            
            if filepath is None:
                break
                
            try:
                latent_dict = self._load_and_process_latent(filepath)
                latents.append(latent_dict["samples"])
                i += 1
            except Exception as e:
                print(f"Error loading latent {filepath}: {str(e)}")
                break
        
        if len(latents) == 0:
            error_msg = f"No batch latents found for: {base_filename}_*"
            print(error_msg)
            default_latent = self._create_default_latent()
            return default_latent, 0
        
        # Concatenate all latents into batch
        batch_tensor = torch.cat(latents, dim=0)
        batch_latent = {"samples": batch_tensor}
        return batch_latent, len(latents)

    def _find_latent_file(self, base_filename):
        """Find latent file with supported extension."""
        input_dir = folder_paths.get_input_directory().replace("\\", "/") + "/"
        
        # If filename already has extension, try it directly
        if any(base_filename.lower().endswith(ext) for ext in self.SUPPORTED_EXTENSIONS):
            filepath = input_dir + base_filename
            if os.path.exists(filepath):
                return filepath
        else:
            # Try with each supported extension
            for ext in self.SUPPORTED_EXTENSIONS:
                filepath = input_dir + base_filename + ext
                if os.path.exists(filepath):
                    return filepath
        
        return None

    def _load_and_process_latent(self, filepath):
        """Load latent tensor from file."""
        # Load the tensor from file
        latent_tensor = torch.load(filepath, map_location='cpu')
        
        # Handle different save formats
        if isinstance(latent_tensor, dict):
            # If it's already in ComfyUI latent format
            if "samples" in latent_tensor:
                return latent_tensor
            else:
                # Assume the tensor is stored under some other key or it's a raw dict
                # Try to find the tensor
                for key, value in latent_tensor.items():
                    if isinstance(value, torch.Tensor):
                        return {"samples": value}
                # If no tensor found, create default
                print(f"Warning: No tensor found in latent file {filepath}")
                return self._create_default_latent()
        elif isinstance(latent_tensor, torch.Tensor):
            # Raw tensor, wrap in ComfyUI format
            return {"samples": latent_tensor}
        else:
            print(f"Warning: Unexpected latent format in {filepath}")
            return self._create_default_latent()

    def _create_default_latent(self):
        """Create a default latent when loading fails."""
        default_tensor = torch.zeros(
            self.DEFAULT_BATCH, 
            self.DEFAULT_CHANNELS, 
            self.DEFAULT_HEIGHT, 
            self.DEFAULT_WIDTH
        )
        return {"samples": default_tensor}
