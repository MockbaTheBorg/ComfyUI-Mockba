"""
Simple node to test python<->javascript communication.
"""

# Local imports
from .common import any_typ

class mbTest:
    def __init__(self):
        """Initialize the test node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input": (any_typ, {}),
                "widget": ("STRING", {"multiline": False})
            }
        }

    # Node metadata
    TITLE = "Test Node"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("output",)
    FUNCTION = "test_object"
    CATEGORY = "unset"
    DESCRIPTION = "A simple node to test python<->javascript communication."
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """Force execution every time by returning a unique value."""
        import time
        return time.time()

    def test_object(self, **kwargs):
        # Print kwargs
        print("Debug Info:", kwargs)
        return {
            "ui": {"value": [kwargs.get("input")]}, # This goes to the Javascript frontend as a message
            "result": (kwargs.get("input"),) # This goes to the outputs
        }
