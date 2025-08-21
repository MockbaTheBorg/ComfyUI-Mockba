"""
Empty Latent Image Generator for ComfyUI
Creates empty latent tensors for diffusion model initialization with device and memory management.
"""

# Standard library imports
import gc
import os

# Third-party imports
import torch

class mbEmptyLatentImage:
    """Generate empty latent images with configurable dimensions and device placement."""
    
    # Class constants
    MAX_RESOLUTION = 4096
    MIN_RESOLUTION = 64
    RESOLUTION_STEP = 8
    LATENT_CHANNELS = 4
    LATENT_SCALE_FACTOR = 8
    MAX_BATCH_SIZE = 64
    
    # Default values
    DEFAULT_WIDTH = 512
    DEFAULT_HEIGHT = 512
    DEFAULT_BATCH_SIZE = 1
    
    # Resolution file path (relative to node location)
    RESOLUTIONS_FILE = "resolutions.txt"
    
    def __init__(self):
        """Initialize the empty latent image generator."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for latent image generation."""
        # Get available devices
        devices = cls._get_available_devices()
        default_device = devices[0]
        
        # Load available resolutions
        resolutions = cls._load_resolutions()
        default_resolution = resolutions[0] if resolutions else "custom"
        
        return {
            "required": {
                "size": (resolutions, {
                    "default": default_resolution,
                    "tooltip": "Predefined resolution or 'custom' for manual width/height"
                }),
                "width": ("INT", {
                    "default": cls.DEFAULT_WIDTH,
                    "min": cls.MIN_RESOLUTION,
                    "max": cls.MAX_RESOLUTION,
                    "step": cls.RESOLUTION_STEP,
                    "tooltip": "Custom width (used when size is 'custom')"
                }),
                "height": ("INT", {
                    "default": cls.DEFAULT_HEIGHT,
                    "min": cls.MIN_RESOLUTION,
                    "max": cls.MAX_RESOLUTION,
                    "step": cls.RESOLUTION_STEP,
                    "tooltip": "Custom height (used when size is 'custom')"
                }),
                "batch_size": ("INT", {
                    "default": cls.DEFAULT_BATCH_SIZE,
                    "min": 1,
                    "max": cls.MAX_BATCH_SIZE,
                    "tooltip": "Number of latent images to generate in batch"
                }),
                "device": (devices, {
                    "default": default_device,
                    "tooltip": "Device to create the latent tensor on (CPU/CUDA)"
                }),
                "memory_management": (["none", "light", "aggressive"], {
                    "default": "none",
                    "tooltip": "Memory cleanup level before tensor creation"
                }),
            }
        }

    # Node metadata
    TITLE = "Empty Latent Image"
    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent_image",)
    FUNCTION = "generate_empty_latent"
    CATEGORY = "unset"
    DESCRIPTION = "Create empty latent tensors for diffusion models with device placement and memory management options."

    def generate_empty_latent(self, size, width, height, batch_size, device, memory_management):
        """
        Generate empty latent image tensor.
        
        Args:
            size: Predefined resolution string or "custom"
            width: Custom width (used when size is "custom")
            height: Custom height (used when size is "custom") 
            batch_size: Number of images in batch
            device: Target device for tensor
            memory_management: Memory cleanup level
            
        Returns:
            tuple: (latent_dict,) containing the empty latent tensor
        """
        try:
            # Perform memory management if requested
            self._perform_memory_cleanup(memory_management, device)
            
            # Determine final dimensions
            final_width, final_height = self._resolve_dimensions(size, width, height)
            
            # Validate dimensions
            self._validate_dimensions(final_width, final_height, batch_size)
            
            # Calculate latent dimensions
            latent_width = final_width // self.LATENT_SCALE_FACTOR
            latent_height = final_height // self.LATENT_SCALE_FACTOR
            
            # Create empty latent tensor
            latent_tensor = self._create_latent_tensor(
                batch_size, latent_height, latent_width, device
            )
            
            print(f"Created empty latent: {batch_size}x{self.LATENT_CHANNELS}x{latent_height}x{latent_width} on {device}")
            
            return ({"samples": latent_tensor},)
            
        except Exception as e:
            error_msg = f"Failed to generate empty latent: {str(e)}"
            print(error_msg)
            # Return a minimal fallback latent
            fallback_latent = torch.zeros([1, self.LATENT_CHANNELS, 64, 64], device="cpu")
            return ({"samples": fallback_latent},)

    @classmethod
    def _get_available_devices(cls):
        """Get list of available compute devices."""
        devices = ["cpu"]
        
        if torch.cuda.is_available():
            # Add CUDA devices
            for i in range(torch.cuda.device_count()):
                devices.append(f"cuda:{i}")
            # Add generic cuda device
            if "cuda:0" in devices:
                devices.insert(1, "cuda")  # Insert after cpu
        
        return devices

    @classmethod
    def _load_resolutions(cls):
        """Load available resolutions from file."""
        resolutions = ["custom"]  # Always include custom option
        
        try:
            # Try multiple possible paths for the resolutions file
            possible_paths = [
                cls.RESOLUTIONS_FILE,
                f"ComfyUI/custom_nodes/ComfyUI-Mockba/{cls.RESOLUTIONS_FILE}",
                f"custom_nodes/ComfyUI-Mockba/{cls.RESOLUTIONS_FILE}",
                os.path.join(os.path.dirname(__file__), "..", cls.RESOLUTIONS_FILE)
            ]
            
            for file_path in possible_paths:
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#"):
                                resolutions.append(line)
                    break
            else:
                # If no file found, add some common resolutions
                common_resolutions = [
                    "512x512", "768x768", "1024x1024",
                    "512x768", "768x512", "1024x768", "768x1024"
                ]
                resolutions.extend(common_resolutions)
                
        except Exception as e:
            print(f"Warning: Could not load resolutions file: {str(e)}")
            # Use fallback resolutions
            resolutions.extend(["512x512", "768x768", "1024x1024"])
        
        return resolutions

    def _perform_memory_cleanup(self, memory_management, device):
        """Perform memory cleanup based on the specified level."""
        if memory_management == "none":
            return
        
        if memory_management in ["light", "aggressive"]:
            gc.collect()
        
        if memory_management == "aggressive" and device.startswith("cuda"):
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                if hasattr(torch.cuda, 'ipc_collect'):
                    torch.cuda.ipc_collect()

    def _resolve_dimensions(self, size, width, height):
        """Resolve final dimensions from size parameter and custom values."""
        if size in ["custom", "------"]:
            return width, height
        
        try:
            # Parse resolution string (e.g., "512x768")
            if "x" in size:
                size_width, size_height = size.split("x", 1)
                return int(size_width), int(size_height)
            else:
                # Fallback to custom dimensions if parsing fails
                return width, height
        except (ValueError, AttributeError):
            print(f"Warning: Could not parse size '{size}', using custom dimensions")
            return width, height

    def _validate_dimensions(self, width, height, batch_size):
        """Validate that dimensions and batch size are reasonable."""
        if width < self.MIN_RESOLUTION or height < self.MIN_RESOLUTION:
            raise ValueError(f"Dimensions too small: {width}x{height} (minimum: {self.MIN_RESOLUTION}x{self.MIN_RESOLUTION})")
        
        if width > self.MAX_RESOLUTION or height > self.MAX_RESOLUTION:
            raise ValueError(f"Dimensions too large: {width}x{height} (maximum: {self.MAX_RESOLUTION}x{self.MAX_RESOLUTION})")
        
        if batch_size < 1 or batch_size > self.MAX_BATCH_SIZE:
            raise ValueError(f"Invalid batch size: {batch_size} (range: 1-{self.MAX_BATCH_SIZE})")
        
        # Ensure dimensions are compatible with latent scale factor
        if width % self.LATENT_SCALE_FACTOR != 0 or height % self.LATENT_SCALE_FACTOR != 0:
            print(f"Warning: Dimensions {width}x{height} not divisible by {self.LATENT_SCALE_FACTOR}, may cause issues")

    def _create_latent_tensor(self, batch_size, latent_height, latent_width, device):
        """Create the empty latent tensor with specified dimensions."""
        try:
            # Validate device availability
            if device.startswith("cuda") and not torch.cuda.is_available():
                print(f"Warning: CUDA not available, falling back to CPU")
                device = "cpu"
            
            # Create tensor
            latent_tensor = torch.zeros(
                [batch_size, self.LATENT_CHANNELS, latent_height, latent_width],
                device=device,
                dtype=torch.float32
            )
            
            return latent_tensor
            
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                print(f"CUDA out of memory, falling back to CPU")
                return torch.zeros(
                    [batch_size, self.LATENT_CHANNELS, latent_height, latent_width],
                    device="cpu",
                    dtype=torch.float32
                )
            else:
                raise e
