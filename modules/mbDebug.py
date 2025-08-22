"""
Debug Information Node for ComfyUI
Displays comprehensive debug information about any input object.
"""

# Standard library imports
from pprint import pformat

# Local imports
from .common import any_typ

class mbDebug:
    """Display comprehensive debug information about any input object."""
    
    # Class constants
    DEFAULT_DEBUG_MESSAGE = "Debug output will appear here after execution..."
    SEPARATOR_LINE = "-" * 40
    
    def __init__(self):
        """Initialize the debug information node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for debug information display."""
        return {
            "required": {
                "input": (any_typ, {
                    "tooltip": "Any object to debug and analyze"
                }),
            }
        }

    # Node metadata
    TITLE = "Debug Information"
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "debug_object"
    CATEGORY = "unset"
    DESCRIPTION = "Display comprehensive debug information about any input object in a text widget."
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """Force execution every time by returning a unique value."""
        import time
        return time.time()

    def debug_object(self, input):
        """
        Generate debug information for the input object.
        
        Args:
            input: Any object to debug
            console_output: Whether to print to console
            truncate_size: Maximum characters for truncation (0 = no truncation)
            
        Returns:
            dict: UI update with formatted debug information
        """
        try:
            debug_lines = self._generate_debug_info(input)
            debug_text = "\n".join(debug_lines)
            
        except Exception as e:
            debug_text = f"Error: {str(e)}"

        return {
            "ui": {"value": [debug_text]},
            "result": (debug_text,)
        }

    def _generate_debug_info(self, obj):
        """Generate comprehensive debug information for an object."""
        debug_lines = []
        debug_lines.append("Debug Info:")
        debug_lines.append(self.SEPARATOR_LINE)
        
        # Check object type and generate appropriate debug info
        if self._is_tensor(obj):
            debug_lines.extend(self._debug_tensor(obj))
        elif self._is_complex_object(obj):
            debug_lines.extend(self._debug_object(obj))
        else:
            debug_lines.extend(self._debug_simple_value(obj))
        
        return debug_lines

    def _is_tensor(self, obj):
        """Check if object is a tensor."""
        return hasattr(obj, 'shape') and hasattr(obj, 'dtype')

    def _is_complex_object(self, obj):
        """Check if object is a complex object (not a simple value)."""
        return (isinstance(obj, object) and 
                not isinstance(obj, (str, int, float, bool, list, dict, tuple)))

    def _debug_tensor(self, tensor):
        """Generate debug information for tensor objects."""
        debug_lines = ["TENSOR INFORMATION:"]
        debug_lines.append(f"  Type: {type(tensor).__name__}")
        debug_lines.append(f"  Shape: {tensor.shape}")
        debug_lines.append(f"  Data type: {tensor.dtype}")
        debug_lines.append(f"  Device: {getattr(tensor, 'device', 'N/A')}")
        debug_lines.append(f"  Requires grad: {getattr(tensor, 'requires_grad', 'N/A')}")
        
        # Add statistical information if possible
        try:
            if hasattr(tensor, 'min') and hasattr(tensor, 'max'):
                debug_lines.append(f"  Min value: {tensor.min().item()}")
                debug_lines.append(f"  Max value: {tensor.max().item()}")
                debug_lines.append(f"  Mean value: {tensor.float().mean().item():.6f}")
        except:
            debug_lines.append("  Statistical info: Unable to compute")
            
        debug_lines.append("")
        return debug_lines

    def _debug_object(self, obj):
        """Generate debug information for complex objects."""
        debug_lines = ["OBJECT INFORMATION:"]
        debug_lines.append(f"  Type: {type(obj).__name__}")
        debug_lines.append("  Available methods and attributes:")
        
        try:
            debug_lines.append(pformat(dir(obj), indent=4))
        except:
            debug_lines.append("    Unable to list attributes")
            
        return debug_lines

    def _debug_simple_value(self, obj):
        """Generate debug information for simple values."""
        debug_lines = ["VALUE INFORMATION:"]
        debug_lines.append(f"  Type: {type(obj).__name__}")
        
        try:
            value_str = str(obj)
            # Note: Truncation is now handled at the top level in debug_object
            debug_lines.append(f"  Value: {value_str}")
        except:
            debug_lines.append("  Value: Unable to convert to string")
            
        return debug_lines
