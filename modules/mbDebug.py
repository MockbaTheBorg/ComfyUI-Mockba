from pprint import pprint
from .common import *

# Shows debug information about the input object.
class mbDebug:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "input": (any_typ, {}),
                "element": ("STRING", {"default": "element name"}),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/tools"
    DESCRIPTION = "Shows debug information about the input object."
    OUTPUT_NODE = True

    def execute(self, input, element):

        print(f"Debug {element}:")
        if isinstance(input, object) and not isinstance(
            input, (str, int, float, bool, list, dict, tuple)
        ):
            print("Objects directory listing:")
            pprint(dir(input), indent=4)
        else:
            print(input)

        return ()
