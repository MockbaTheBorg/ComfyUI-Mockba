from .common import any_typ
from .wireless_registry import store_wireless_data, retrieve_wireless_data, get_wireless_ids

class mbWirelessRelay:
    """
    Wireless Relay Node - Combines input and output with guaranteed execution order
    """
    
    TITLE = "📡 Wireless Relay"
    CATEGORY = "🖖 Mockba/data"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["transmit", "receive"], {"default": "transmit"}),
                "id": ("STRING", {"default": "wireless_1", "multiline": False}),
            },
            "optional": {
                "data": (any_typ, {}),  # Required for transmit mode
            }
        }
    
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("output",)
    FUNCTION = "relay"
    
    def relay(self, mode, id, data=None):
        """
        Either transmit or receive data based on mode
        """
        if mode == "transmit":
            if data is None:
                raise ValueError("Data input is required in transmit mode")
            # Store and pass through
            stored_data = store_wireless_data(id, data)
            return (stored_data,)
            
        elif mode == "receive":
            # Retrieve data
            retrieved_data = retrieve_wireless_data(id)
            return (retrieved_data,)
        
        else:
            raise ValueError(f"Invalid mode: {mode}")
