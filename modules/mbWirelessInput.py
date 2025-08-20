from .common import any_typ
from .wireless_registry import store_wireless_data

class mbWirelessInput:
    """
    Wireless Input Node - Stores data with an ID for wireless transmission
    """
    
    TITLE = "📡 Wireless Input"
    CATEGORY = "🖖 Mockba/data"
    OUTPUT_NODE = True  # Force execution even without downstream connections
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "id": ("STRING", {"default": "1", "multiline": False}),
                "data": (any_typ, {}),
            }
        }
    
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("passthrough",)
    FUNCTION = "transmit"
    
    @classmethod
    def IS_CHANGED(cls, id, data, **kwargs):
        """
        Tell ComfyUI when this node needs to re-execute.
        This ensures fresh data is stored when inputs change.
        """
        import hashlib
        import time
        
        try:
            # Create a unique hash based on the data content
            if hasattr(data, 'shape'):  # For tensors/numpy arrays
                # For images/tensors, use shape, dtype, and sample values
                data_str = f"{data.shape}_{data.dtype}_{str(data.flatten()[:20].tolist())}"
            elif hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                data_str = str(data)[:1000]  # Limit for performance
            else:
                data_str = str(data)
            
            # Include ID to make it unique per wireless connection
            content_str = f"{id}_{data_str}"
            content_hash = hashlib.md5(content_str.encode()).hexdigest()
            
            print(f"[Wireless Input] Change detection for '{id}': {content_hash[:8]}")
            return content_hash
            
        except Exception as e:
            # Fallback: always re-execute if we can't compute hash
            print(f"[Wireless Input] Hash computation failed for '{id}', forcing re-execution: {e}")
            return float("NaN")
    
    def transmit(self, id, data):
        """
        Store data in global registry and pass it through
        """
        # Store in global registry using centralized function
        stored_data = store_wireless_data(id, data)
        
        # Pass through the data so it can still be used locally
        return (stored_data,)
