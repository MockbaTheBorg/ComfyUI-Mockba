from .common import any_typ
from .wireless_registry import retrieve_wireless_data, get_wireless_ids, get_data_hash

class mbWirelessOutput:
    """
    Wireless Output Node - Receives data from a Wireless Input with matching ID
    """
    
    TITLE = "📡 Wireless Output"
    CATEGORY = "🖖 Mockba/data"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "id": ("STRING", {"default": "wireless_1", "multiline": False}),
            }
        }
    
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("data",)
    FUNCTION = "receive"
    
    @classmethod
    def IS_CHANGED(cls, id, **kwargs):
        """
        Tell ComfyUI when this node needs to re-execute.
        This checks if the wireless input data has changed.
        """
        if not id or not id.strip():
            return float("NaN")
        
        id = id.strip()
        
        # Get the current hash of the data stored with this ID
        data_hash = get_data_hash(id)
        print(f"[Wireless Output] Current data hash for '{id}': {data_hash[:8] if data_hash != 'not_found' else 'not_found'}")
        
        # Return the hash - if it changes, ComfyUI will re-execute this node
        return data_hash
    
    @classmethod
    def VALIDATE_INPUTS(cls, id, **kwargs):
        """
        Validate that the wireless input with this ID exists.
        This runs before execution and can influence scheduling.
        """
        from .wireless_registry import get_wireless_registry
        
        if not id or not id.strip():
            return "Wireless ID cannot be empty"
        
        id = id.strip()
        registry = get_wireless_registry()
        
        # Don't fail validation - just log the state
        print(f"[Wireless Output Validation] ID: '{id}', Registry has: {list(registry.keys())}")
        
        return True  # Always pass validation to allow execution
    
    def receive(self, id):
        """
        Retrieve data from global registry by ID
        """
        # Use centralized retrieval function with enhanced debugging
        data = retrieve_wireless_data(id)
        return (data,)
