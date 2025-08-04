import os
import folder_paths

# loads text from a file or uses the entered value.
class mbTextOrFile:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "input": ("STRING", {"default": "", "multiline": True}),
                "filename": ("STRING", {"default": "filename.txt"}),
                "action": (["append", "prepend", "replace"], {"default": "append"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/file"
    DESCRIPTION = "Loads text from a file or uses the entered value."

    def execute(self, input, filename, action):
        prefix = folder_paths.get_input_directory()
        prefix = prefix.replace("\\", "/") + "/"
        if not os.path.exists(prefix):
            os.makedirs(prefix)
            
        # Ensure .txt extension if not present
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
            
        filepath = prefix + filename
        if not os.path.exists(filepath):
            return (input,)
        with open(filepath, "r") as f:
            file_text = f.read()
        if action == "append":
            file_text = file_text + input
        elif action == "prepend":
            file_text = input + file_text
        elif action == "replace":
            file_text = input
        print("Loaded: " + filepath)
        return (file_text,)
