"""
Submit Node for ComfyUI
Provides workflow submission controls with optional data passthrough.
"""

# Local imports
from .common import any_typ, CATEGORIES


class mbSubmit:
    """Workflow submission node with optional data passthrough capability."""
    
    def __init__(self):
        """Initialize the submit node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for workflow submission."""
        return {
            "required": {},
        }

    # Node metadata
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "submit_workflow"
    CATEGORY = CATEGORIES["DEVELOPMENT"]
    DESCRIPTION = "Workflow submission node with button interface. Submission handled by JavaScript interface."
    OUTPUT_NODE = True

    def submit_workflow(self):
        """
        Handle workflow submission trigger.
        
        Note:
            Actual workflow submission is handled by JavaScript interface.
            This node serves as a UI trigger point for submission buttons.
        """
        # This node doesn't perform actual submission in Python
        # The submission functionality is handled by JavaScript buttons
        # This function just serves as a trigger point
        return ()
