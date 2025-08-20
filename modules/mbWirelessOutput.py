"""
Wireless Output Node for ComfyUI
Retrieves data from file cache transmitted by Wireless Input nodes.
"""

# Standard library imports
import os
import pickle

# ComfyUI imports
import folder_paths

# Local imports
from .common import any_typ, CATEGORIES


class mbWirelessOutput:
    """Retrieve data from file cache for wireless transmission."""
    
    # Class constants
    DEFAULT_CHANNEL = 1
    MIN_CHANNEL = 1
    MAX_CHANNEL = 8
    CHANNEL_STEP = 1
    CACHE_FOLDER = "wireless_cache"
    
    def __init__(self):
        """Initialize the wireless output node."""
        self.cache_dir = self._get_cache_directory()

    def _get_cache_directory(self):
        """Get the wireless cache directory path."""
        temp_dir = folder_paths.get_temp_directory()
        return os.path.join(temp_dir, self.CACHE_FOLDER)
    
    def _get_cache_file_path(self, channel):
        """Get the cache file path for a specific channel."""
        return os.path.join(self.cache_dir, f"channel_{channel}.pkl")

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for wireless output."""
        return {
            "required": {
                "channel": ("INT", {
                    "default": cls.DEFAULT_CHANNEL,
                    "min": cls.MIN_CHANNEL,
                    "max": cls.MAX_CHANNEL,
                    "step": cls.CHANNEL_STEP,
                    "tooltip": "Wireless channel (1-8) to receive data from"
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    # Node metadata
    TITLE = "📡 Wireless Output"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("data",)
    FUNCTION = "receive_data"
    CATEGORY = "unset"
    DESCRIPTION = "Retrieve data from file cache transmitted by wireless input nodes."
    
    @classmethod
    def IS_CHANGED(cls, channel, **kwargs):
        """Check if the cache file for this channel has been updated."""
        import time
        import os
        try:
            # Get the cache file path
            temp_dir = folder_paths.get_temp_directory()
            cache_dir = os.path.join(temp_dir, cls.CACHE_FOLDER)
            cache_file = os.path.join(cache_dir, f"channel_{channel}.pkl")
            
            # Return modification time if file exists, otherwise current time
            if os.path.exists(cache_file):
                mtime = os.path.getmtime(cache_file)
                return f"ch{channel}_{mtime}"
            else:
                return f"ch{channel}_nofile_{time.time()}"
        except Exception:
            return str(time.time())

    def receive_data(self, channel, **kwargs):
        """
        Retrieve data from file cache for the specified channel.
        
        Args:
            channel: Channel number (1-8) for wireless reception
            **kwargs: Additional arguments (unique_id, extra_pnginfo)
            
        Returns:
            tuple: Retrieved data from cache, or None if not available
        """
        import time
        
        # Retry mechanism to handle timing issues
        max_retries = 3
        retry_delay = 0.1  # 100ms between retries
        
        for attempt in range(max_retries):
            try:
                # Get cache file path
                cache_file = self._get_cache_file_path(channel)
                
                # Check if cache file exists
                if not os.path.exists(cache_file):
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    print(f"mbWirelessOutput: No data available on channel {channel} (cache file not found)")
                    return (None,)
                
                # Load data from cache file
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                
                if data is None:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    print(f"mbWirelessOutput: No data available on channel {channel} (empty cache)")
                    return (None,)
                else:
                    print(f"mbWirelessOutput: Retrieved data from channel {channel} (type: {type(data).__name__})")
                    return (data,)
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                error_msg = f"Failed to receive data from channel {channel}: {str(e)}"
                print(f"mbWirelessOutput: {error_msg}")
                return (None,)
        
        return (None,)
