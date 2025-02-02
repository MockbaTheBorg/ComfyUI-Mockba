import os
import folder_paths

# Saves text to a file.
class mbTextToFile:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "text": ("STRING", {"default": "text"}),
                "base_name": ("STRING", {"default": "text"}),
                "id": ("INT", {"default": 0, "min": 0, "step": 1}),
                "use_id": (["yes", "no"], {"default": "no"}),
            },
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
    DESCRIPTION = "Saves text to a file."

    def execute(self, text, base_name, id, use_id):
        prefix = folder_paths.get_input_directory()
        prefix = prefix.replace("\\", "/") + "/"
        if not os.path.exists(prefix):
            os.makedirs(prefix)
        if use_id == "yes":
            filename = base_name + "_" + str(id) + ".txt"
        else:
            filename = base_name + ".txt"
        with open(prefix + filename, "w") as f:
            f.write(text)
        print("Saved: " + prefix + filename)
        return (
            text,
            id,
        )
