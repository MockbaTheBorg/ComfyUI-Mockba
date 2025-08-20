from .wireless_registry import get_wireless_ids, clear_wireless_registry, get_registry_info

class mbWirelessManager:
    """
    Wireless Manager Node - Utility for managing the wireless registry
    """
    
    TITLE = "📡 Wireless Manager"
    CATEGORY = "🖖 Mockba/development"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "action": (["list_ids", "clear_registry", "count_entries"], {"default": "list_ids"}),
            },
            "optional": {
                "trigger": ("*", {}),  # Any input to trigger execution
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("info",)
    FUNCTION = "manage"
    OUTPUT_NODE = True
    
    def manage(self, action, trigger=None):
        """
        Manage wireless registry and return info
        """
        info = ""  # Initialize info variable
        
        if action == "list_ids":
            ids = get_wireless_ids()
            if ids:
                info = f"Active wireless IDs: {', '.join(ids)}"
            else:
                info = "No active wireless connections"
                
        elif action == "clear_registry":
            registry_info = get_registry_info()
            count = registry_info["count"]
            clear_wireless_registry()
            info = f"Cleared {count} wireless entries"
            
        elif action == "count_entries":
            registry_info = get_registry_info()
            count = registry_info["count"]
            info = f"Wireless registry contains {count} entries"
        
        else:
            info = f"Unknown action: {action}"
        
        print(f"[Wireless Manager] {info}")
        return (info,)
