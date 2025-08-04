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
                "filename": ("STRING", {"default": "input.txt"}),
            },
            "optional": {
                "default_text": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = (
        "STRING",
    )
    RETURN_NAMES = (
        "text",
    )
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/file"
    DESCRIPTION = "Loads text from a file."

    def execute(self, filename, default_text=""):
        # If default text is provided and not empty, return it instead of reading file
        if default_text and default_text.strip():
            return (default_text,)
            
        prefix = folder_paths.get_input_directory()
        prefix = prefix.replace("\\", "/") + "/"
        
        # Ensure .txt extension if not present
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
            
        filepath = prefix + filename
        
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return (default_text,)
            
        try:
            with open(filepath, "r", encoding='utf-8') as f:
                text = f.read()
            print(f"Loaded: {filepath}")
            return (text,)
        except Exception as e:
            print(f"Error reading file {filepath}: {str(e)}")
            return (default_text,)
