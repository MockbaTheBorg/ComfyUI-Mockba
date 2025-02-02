import os
import folder_paths

# Loads text from a file.
class mbFileToText:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "default": ("STRING", {"default": ""}),
                "base_name": ("STRING", {"default": "text"}),
                "id": ("INT", {"default": 0, "min": 0, "step": 1}),
                "use_id": (["yes", "no"], {"default": "no"}),
            }
        }

    RETURN_TYPES = (
        "STRING",
        "INT",
    )
    RETURN_NAMES = (
        "text",
        "id",
    )
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/file"
    DESCRIPTION = "Loads text from a file."

    def execute(self, default, base_name, id, use_id):
        if default != "":
            return (default, id)
        prefix = folder_paths.get_input_directory()
        prefix = prefix.replace("\\", "/") + "/"
        if use_id == "yes":
            filename = base_name + "_" + str(id) + ".txt"
        else:
            filename = base_name + ".txt"
        if not os.path.exists(prefix + filename):
            return ("",)
        with open(prefix + filename, "r") as f:
            text = f.read()
        print("Loaded: " + prefix + filename)
        return (
            text,
            id,
        )
