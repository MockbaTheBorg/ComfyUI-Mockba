import torch
from .common import any_typ

class mbDeviceTransfer:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        # Get available devices
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
        
        return {
            "required": {
                "tensor": (any_typ, {}),
                "device": (devices, {"default": "cpu"}),
            }
        }

    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("tensor",)
    FUNCTION = "transfer_device"
    CATEGORY = "🖖 Mockba/utility"
    DESCRIPTION = "Transfer tensor to specified device (CPU, CUDA, MPS)"

    def transfer_device(self, tensor, device):
        try:
            # Check if input has a device attribute (is a tensor)
            if hasattr(tensor, 'device') and hasattr(tensor, 'to'):
                # It's a PyTorch tensor, transfer it
                transferred_tensor = tensor.to(device)
                return (transferred_tensor,)
            else:
                # Not a tensor, return as-is
                print(f"Warning: Input is not a tensor (type: {type(tensor)}), returning unchanged")
                return (tensor,)
                
        except Exception as e:
            print(f"Error transferring tensor to device {device}: {str(e)}")
            # Return original tensor on error
            return (tensor,)
