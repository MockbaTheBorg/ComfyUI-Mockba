from .common import any_typ
from .wireless_registry import retrieve_wireless_data, get_data_hash

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
        Always force execution to avoid one-cycle lag.
        """
        if not id or not id.strip():
            return float("NaN")  # still guard against empty id

        # We still log the current hash for debugging insight.
        sid = id.strip()
        data_hash = get_data_hash(sid)
        print(f"[Wireless Output] (forced) current data hash for '{sid}': {data_hash[:8] if data_hash != 'not_found' else 'not_found'}")

        # Return a unique value every call (time-based) so ComfyUI always re-runs.
        import time
        return time.time()
    
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
