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
                "filename": ("STRING", {"default": "output.txt"}),
            },
        }

    RETURN_TYPES = (
        "STRING",
    )
    RETURN_NAMES = (
        "text",
    )
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/file"
    DESCRIPTION = "Saves text to a file."

    def execute(self, text, filename):
        prefix = folder_paths.get_input_directory()
        prefix = prefix.replace("\\", "/") + "/"
        if not os.path.exists(prefix):
            os.makedirs(prefix)
        
        # Ensure .txt extension if not present
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
            
        filepath = prefix + filename
        with open(filepath, "w") as f:
            f.write(text)
        print("Saved: " + filepath)
        return (text,)
