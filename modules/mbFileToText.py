"""
File to Text Reader Node for ComfyUI
Loads text content from files with fallback to default text.
"""

# Standard library imports
import os

# ComfyUI imports
import folder_paths

# Local imports
from .common import CATEGORIES


class mbFileToText:
    """Load text content from files with automatic fallback handling."""
    
    # Class constants
    DEFAULT_FILENAME = "input.txt"
    DEFAULT_TEXT = ""
    TEXT_EXTENSION = ".txt"
    ENCODING = "utf-8"
    
    def __init__(self):
        """Initialize the file to text reader node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for text file reading."""
        return {
            "required": {
                "filename": ("STRING", {
                    "default": cls.DEFAULT_FILENAME,
                    "tooltip": "Filename to read (.txt extension added automatically)"
                }),
            },
            "optional": {
                "default_text": ("STRING", {
                    "default": cls.DEFAULT_TEXT,
                    "multiline": True,
                    "tooltip": "Default text to return if file doesn't exist or reading fails"
                }),
            }
        }

    # Node metadata
    TITLE = "File to Text Reader"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "load_text_from_file"
    CATEGORY = "unset"
    DESCRIPTION = "Load text content from files with automatic fallback to default text."

    def load_text_from_file(self, filename, default_text=""):
        """
        Load text from file with fallback handling.
        
        Args:
            filename: Name of file to read (extension added automatically)
            default_text: Fallback text if file operations fail
            
        Returns:
            tuple: Loaded text content or default text
        """
        try:
            # If default text is provided and not empty, return it instead of reading file
            if self._should_use_default_text(default_text):
                return (default_text,)
            
            # Prepare file path
            filepath = self._prepare_filepath(filename)
            
            # Load text from file
            text_content = self._load_text_file(filepath, default_text)
            
            return (text_content,)
            
        except Exception as e:
            error_msg = f"Unexpected error in file to text: {str(e)}"
            print(error_msg)
            return (default_text,)

    def _should_use_default_text(self, default_text):
        """Check if default text should be used instead of file reading."""
        return default_text and default_text.strip()

    def _prepare_filepath(self, filename):
        """Prepare the full file path with proper extension."""
        prefix = folder_paths.get_input_directory()
        prefix = prefix.replace("\\", "/") + "/"
        
        # Ensure .txt extension
        if not filename.endswith(self.TEXT_EXTENSION):
            filename = filename + self.TEXT_EXTENSION
            
        return prefix + filename

    def _load_text_file(self, filepath, fallback_text):
        """Load text from file with error handling."""
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return fallback_text
            
        try:
            with open(filepath, "r", encoding=self.ENCODING) as f:
                text = f.read()
            print(f"Text loaded from: {filepath}")
            return text
        except Exception as e:
            print(f"Error reading file {filepath}: {str(e)}")
            return fallback_text
