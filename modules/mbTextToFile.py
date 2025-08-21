"""
Text to File Writer Node for ComfyUI
Saves text content to files with automatic directory management and extension handling.
"""

# Standard library imports
import os

# ComfyUI imports
import folder_paths

class mbTextToFile:
    """Save text content to files with automatic formatting and path management."""
    
    # Class constants
    DEFAULT_TEXT = "text"
    DEFAULT_FILENAME = "output.txt"
    TEXT_EXTENSION = ".txt"
    ENCODING = "utf-8"
    
    def __init__(self):
        """Initialize the text to file writer node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for text file writing."""
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
                "filename": ("STRING", {
                    "default": cls.DEFAULT_FILENAME,
                    "tooltip": "Filename for saved text (.txt extension added automatically)"
                }),
            },
        }

    # Node metadata
    TITLE = "Text to File Writer"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "save_text_to_file"
    CATEGORY = "unset"
    DESCRIPTION = "Save text content to files with automatic directory management and extension handling."

    def save_text_to_file(self, text, filename):
        """
        Save text content to a file.
        
        Args:
            text: Text content to save
            filename: Target filename (extension added automatically)
            
        Returns:
            tuple: The original text content
        """
        try:
            # Prepare file path
            filepath = self._prepare_filepath(filename)
            
            # Write text to file
            self._write_text_file(filepath, text)
            
            print(f"Text saved to: {filepath}")
            return (text,)
            
        except Exception as e:
            error_msg = f"Failed to save text to file: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)

    def _prepare_filepath(self, filename):
        """Prepare the full file path with directory creation."""
        # Get input directory from ComfyUI
        prefix = folder_paths.get_input_directory()
        prefix = prefix.replace("\\", "/") + "/"
        
        # Create directory if it doesn't exist
        if not os.path.exists(prefix):
            os.makedirs(prefix)
        
        # Ensure .txt extension
        if not filename.endswith(self.TEXT_EXTENSION):
            filename = filename + self.TEXT_EXTENSION
            
        return prefix + filename

    def _write_text_file(self, filepath, text):
        """Write text content to file with proper encoding."""
        with open(filepath, "w", encoding=self.ENCODING) as f:
            f.write(text)
