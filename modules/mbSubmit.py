from .common import *

class mbSubmit:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "input": (any_typ, {}),  # Optional passthrough input
            }
        }

    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("output",)
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/tools"
    DESCRIPTION = "A node with buttons to submit the workflow to the queue."
    OUTPUT_NODE = True

    def execute(self, input=None):
        # This node doesn't do anything in Python - the buttons handle submission in JavaScript
        # It just passes through the input if provided, or returns None
        return (input,)
