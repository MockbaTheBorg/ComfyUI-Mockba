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
            "optional": {
                "input": (any_typ, {
                    "tooltip": "Optional data to pass through the node"
                }),
            }
        }

    # Node metadata
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("output",)
    FUNCTION = "submit_workflow"
    CATEGORY = CATEGORIES["DEVELOPMENT"]
    DESCRIPTION = "Workflow submission node with optional data passthrough. Submission handled by JavaScript interface."
    OUTPUT_NODE = True

    def submit_workflow(self, input=None):
        """
        Handle workflow submission with optional data passthrough.
        
        Args:
            input: Optional data to pass through the node
            
        Returns:
            tuple: Passthrough data or None
            
        Note:
            Actual workflow submission is handled by JavaScript interface.
            This node primarily serves as a passthrough with submission UI.
        """
        # This node doesn't perform actual submission in Python
        # The submission functionality is handled by JavaScript buttons
        # This function just passes through the input data
        return (input,)
