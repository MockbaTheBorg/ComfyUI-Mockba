"""
Device Transfer Node for ComfyUI
Transfers tensors between available compute devices (CPU, CUDA, MPS).
"""

# Standard library imports
import torch

# Local imports
from .common import any_typ, CATEGORIES


class mbDeviceTransfer:
    """Transfer tensors between available compute devices."""
    
    # Class constants
    DEFAULT_DEVICE = "cpu"
    
    def __init__(self):
        """Initialize the device transfer node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types with dynamically detected available devices."""
        devices = cls._get_available_devices()
        
        return {
            "required": {
                "tensor": (any_typ, {
                    "tooltip": "Tensor to transfer between devices"
                }),
                "device": (devices, {
                    "default": cls.DEFAULT_DEVICE,
                    "tooltip": "Target device for tensor transfer"
                }),
            }
        }

    # Node metadata
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("tensor",)
    FUNCTION = "transfer_device"
    CATEGORY = CATEGORIES["DATA_MANAGEMENT"]
    DESCRIPTION = "Transfer tensor to specified device (CPU, CUDA, MPS) for memory optimization and compute efficiency."

    @classmethod
    def _get_available_devices(cls):
        """Detect and return list of available compute devices."""
        devices = ["cpu"]
        
        # Check for CUDA devices
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                devices.append(f"cuda:{i}")
                if i == 0:
                    devices.append("cuda")  # Default CUDA device
        
        # Check for MPS (Apple Silicon) if available
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            devices.append("mps")
        
        return devices

    def transfer_device(self, tensor, device):
        """
        Transfer tensor to the specified device.
        
        Args:
            tensor: Input tensor or data to transfer
            device: Target device string
            
        Returns:
            tuple: Transferred tensor or original data if not transferrable
        """
        try:
            # Validate that input is a transferrable tensor
            if not self._is_transferrable_tensor(tensor):
                print(f"Warning: Input is not a tensor (type: {type(tensor)}), returning unchanged")
                return (tensor,)
            
            # Perform device transfer
            transferred_tensor = self._perform_transfer(tensor, device)
            
            return (transferred_tensor,)
            
        except Exception as e:
            error_msg = f"Error transferring tensor to device {device}: {str(e)}"
            print(error_msg)
            # Return original tensor on error
            return (tensor,)

    def _is_transferrable_tensor(self, obj):
        """Check if object is a PyTorch tensor that can be transferred."""
        return hasattr(obj, 'device') and hasattr(obj, 'to')

    def _perform_transfer(self, tensor, device):
        """Perform the actual device transfer with validation."""
        # Validate device exists
        if device.startswith('cuda') and not torch.cuda.is_available():
            raise RuntimeError(f"CUDA not available, cannot transfer to {device}")
        
        if device == 'mps' and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
            raise RuntimeError("MPS not available, cannot transfer to MPS device")
        
        # Perform transfer
        return tensor.to(device)
