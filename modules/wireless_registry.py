"""
Centralized wireless registry for ComfyUI-Mockba wireless nodes
"""
import hashlib
import time

# Global wireless data registry
# This stores data with ID as key, data as value
_WIRELESS_REGISTRY = {}

# Track execution order and dependencies
_EXECUTION_TRACKER = {}

# Track data changes for cache invalidation
_DATA_HASHES = {}

def get_wireless_registry():
    """Get the global registry dictionary"""
    return _WIRELESS_REGISTRY

def clear_wireless_registry():
    """Clear all wireless data - useful for fresh workflow runs"""
    global _WIRELESS_REGISTRY, _EXECUTION_TRACKER, _DATA_HASHES
    _WIRELESS_REGISTRY.clear()
    _EXECUTION_TRACKER.clear()
    _DATA_HASHES.clear()
    print("[Wireless] Registry, execution tracker, and data hashes cleared")

def get_wireless_ids():
    """Get list of all active wireless IDs"""
    return list(_WIRELESS_REGISTRY.keys())

def _compute_data_hash(id, data):
    """Compute a hash for the data to detect changes"""
    try:
        if hasattr(data, 'shape'):  # For tensors/numpy arrays
            # For tensors, use shape, dtype, and a sample of values
            data_str = f"{data.shape}_{data.dtype}_{str(data.flatten()[:20].tolist())}"
        elif hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
            # For lists, tuples, etc.
            data_str = str(data)[:1000]  # Limit length for performance
        else:
            # For basic types
            data_str = str(data)
        
        # Include ID to make it unique per wireless connection
        content_str = f"{id}_{data_str}"
        return hashlib.md5(content_str.encode()).hexdigest()
        
    except Exception as e:
        # Fallback: use data ID for guaranteed uniqueness per object
        return hashlib.md5(f"fallback_{id}_{id(data)}".encode()).hexdigest()

def store_wireless_data(id, data):
    """Store data in the wireless registry"""
    if not id or not id.strip():
        raise ValueError("Wireless ID cannot be empty")
    
    id = id.strip()
    
    # Compute hash for change detection
    data_hash = _compute_data_hash(id, data)
    
    # Store data and tracking info
    _WIRELESS_REGISTRY[id] = data
    _EXECUTION_TRACKER[id] = True
    _DATA_HASHES[id] = data_hash
    
    print(f"[Wireless] Stored data with ID: '{id}' (type: {type(data).__name__}, hash: {data_hash[:8]}) - Total entries: {len(_WIRELESS_REGISTRY)}")
    return data

def retrieve_wireless_data(id, wait_for_input=True):
    """Retrieve data from the wireless registry"""
    if not id or not id.strip():
        raise ValueError("Wireless ID cannot be empty")
    
    id = id.strip()
    
    # Debug: Show registry state
    print(f"[Wireless] Attempting to retrieve ID: '{id}'")
    print(f"[Wireless] Current registry: {list(_WIRELESS_REGISTRY.keys())}")
    print(f"[Wireless] Execution tracker: {_EXECUTION_TRACKER}")
    
    if id not in _WIRELESS_REGISTRY:
        available_ids = get_wireless_ids()
        if available_ids:
            raise ValueError(f"No wireless input found with ID: '{id}'. Available IDs: {available_ids}")
        else:
            raise ValueError(f"No wireless input found with ID: '{id}'. No wireless inputs have been executed yet.")
    
    data = _WIRELESS_REGISTRY[id]
    hash_info = _DATA_HASHES.get(id, "unknown")
    print(f"[Wireless] Retrieved data with ID: '{id}' (type: {type(data).__name__}, hash: {hash_info[:8]})")
    return data

def get_data_hash(id):
    """Get the current data hash for an ID"""
    return _DATA_HASHES.get(id, "not_found")

def get_registry_info():
    """Get registry information for debugging"""
    return {
        "count": len(_WIRELESS_REGISTRY),
        "ids": list(_WIRELESS_REGISTRY.keys()),
        "registry_id": id(_WIRELESS_REGISTRY),
        "execution_tracker": dict(_EXECUTION_TRACKER),
        "data_hashes": dict(_DATA_HASHES)
    }
