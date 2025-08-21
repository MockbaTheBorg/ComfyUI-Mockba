"""
Wireless Input Node for ComfyUI
Stores any data to a file cache for transmission to Wireless Output nodes.
"""

# Standard library imports
import os
import pickle

# ComfyUI imports
import folder_paths

# Local imports
from .common import any_typ

class mbWirelessInput:
    """Store any data to file cache for wireless transmission."""
    
    # Class constants
    DEFAULT_CHANNEL = 1
    MIN_CHANNEL = 1
    MAX_CHANNEL = 8
    CHANNEL_STEP = 1
    CACHE_FOLDER = "wireless_cache"
    
    # Initialize the cache directory
    def __init__(self):
        """Initialize the wireless input node."""
        self.cache_dir = self._get_cache_directory()
        self._ensure_cache_directory_exists()

    # Get the cache directory path
    def _get_cache_directory(self):
        """Get the wireless cache directory path."""
        temp_dir = folder_paths.get_temp_directory()
        return os.path.join(temp_dir, self.CACHE_FOLDER)

    # Ensure the cache directory exists
    def _ensure_cache_directory_exists(self):
        """Ensure the cache directory exists."""
        os.makedirs(self.cache_dir, exist_ok=True)

    # Get the cache file path for a specific channel
    def _get_cache_file_path(self, channel):
        """Get the cache file path for a specific channel."""
        return os.path.join(self.cache_dir, f"channel_{channel}.pkl")

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for wireless input."""
        return {
            "required": {
                "channel": ("INT", {
                    "default": cls.DEFAULT_CHANNEL,
                    "min": cls.MIN_CHANNEL,
                    "max": cls.MAX_CHANNEL,
                    "step": cls.CHANNEL_STEP,
                    "tooltip": "Wireless channel (1-8) for pairing with output"
                }),
                "data": (any_typ, {
                    "tooltip": "Any data to transmit wirelessly"
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    # Node metadata
    TITLE = "📡 Wireless Input"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("passthrough",)
    FUNCTION = "transmit_data"
    CATEGORY = "unset"
    DESCRIPTION = "Store any data to file cache for wireless transmission to output nodes."
    OUTPUT_NODE = True
    
    @classmethod
    def IS_CHANGED(cls, channel, data, **kwargs):
        """Always mark as changed to ensure execution on every run."""
        import time
        import hashlib
        try:
            # Create a hash of the data for change detection
            data_str = str(data) if data is not None else "None"
            data_hash = hashlib.md5(data_str.encode()).hexdigest()
            timestamp = str(time.time())
            return f"ch{channel}_{data_hash}_{timestamp}"
        except Exception:
            return str(time.time())

    def transmit_data(self, channel, data, unique_id=None, **kwargs):
        """
        Store data to file cache for the specified channel.
        
        Args:
            channel: Channel number (1-8) for wireless transmission
            data: Any data to transmit
            unique_id: Unique workflow/session/run id (from ComfyUI hidden input)
            **kwargs: Additional arguments (extra_pnginfo)
            
        Returns:
            tuple: Passthrough of the input data
        """
        try:
            # Ensure cache directory exists
            self._ensure_cache_directory_exists()
            
            # Get cache file path
            cache_file = self._get_cache_file_path(channel)
            
            # Store data to cache file with atomic write (no control file)
            temp_file = cache_file + ".tmp"
            with open(temp_file, 'wb') as f:
                pickle.dump(data, f)
            import shutil
            shutil.move(temp_file, cache_file)
            print(f"mbWirelessInput: Stored data to channel {channel} (type: {type(data).__name__})")
            return (data,)
        except Exception as e:
            error_msg = f"Failed to transmit data on channel {channel}: {str(e)}"
            print(f"mbWirelessInput: {error_msg}")
            return (data,)  # Return input data even if caching fails
