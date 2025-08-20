from .wireless_registry import get_registry_info, get_wireless_ids

class mbWirelessDebug:
    """
    Wireless Debug Node - Shows current wireless registry state
    """
    
    TITLE = "🔍 Wireless Debug"
    CATEGORY = "🖖 Mockba/development"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "trigger": ("*", {}),  # Any input to trigger execution
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("debug_info",)
    FUNCTION = "debug"
    OUTPUT_NODE = True
    
    def debug(self, trigger=None):
        """
        Show current wireless registry state for debugging
        """
        registry_info = get_registry_info()
        ids = get_wireless_ids()
        
        debug_info = f"""
=== WIRELESS DEBUG INFO ===
Registry ID: {registry_info['registry_id']}
Total Entries: {registry_info['count']}
Active IDs: {ids if ids else 'None'}
Registry State: {'Populated' if ids else 'Empty'}
========================
"""
        
        print(debug_info)
        return (debug_info,)
