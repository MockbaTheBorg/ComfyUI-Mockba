"""
Text or File Input Node for ComfyUI
Loads text from a file and combines it with input text in various ways.
"""

# Standard library imports
import os

# ComfyUI imports
import folder_paths

# Local imports
from .common import CATEGORIES


class mbTextOrFile:
    """Load text from file and combine with input text using various merge actions."""
    
    # Class constants
    DEFAULT_FILENAME = "filename.txt"
    DEFAULT_ENCODING = "utf-8"
    SUPPORTED_ACTIONS = ["append", "prepend", "replace", "use_input_only"]
    
    def __init__(self):
        """Initialize the text or file input node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for text/file operations."""
        return {
            "required": {
                "input_text": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Text input to combine with file content"
                }),
                "filename": ("STRING", {
                    "default": cls.DEFAULT_FILENAME,
                    "tooltip": "Name of the text file to load (will add .txt if no extension)"
                }),
                "action": (cls.SUPPORTED_ACTIONS, {
                    "default": "append",
                    "tooltip": "How to combine file and input text"
                }),
                "fallback_mode": (["use_input", "empty_string"], {
                    "default": "use_input",
                    "tooltip": "What to return if file doesn't exist"
                }),
            },
        }

    # Node metadata
    TITLE = "Text or File Input"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "process_text_or_file"
    CATEGORY = CATEGORIES["FILE_OPS"]
    DESCRIPTION = "Load text from file and combine with input text using append, prepend, replace, or input-only modes."

    def process_text_or_file(self, input_text, filename, action, fallback_mode):
        """
        Process text input and file content based on specified action.
        
        Args:
            input_text: Text input from user
            filename: Name of file to load
            action: How to combine texts (append, prepend, replace, use_input_only)
            fallback_mode: What to return if file doesn't exist
            
        Returns:
            tuple: (combined_text,)
        """
        try:
            # Handle input-only mode early
            if action == "use_input_only":
                return (input_text,)
            
            # Prepare file path
            filepath = self._prepare_filepath(filename)
            
            # Load file content
            file_content = self._load_file_content(filepath)
            
            if file_content is None:
                # File doesn't exist, handle fallback
                return self._handle_file_not_found(input_text, fallback_mode, filepath)
            
            # Combine texts based on action
            result_text = self._combine_texts(file_content, input_text, action)
            
            print(f"Text processed from file: {filepath}")
            return (result_text,)
            
        except Exception as e:
            error_msg = f"Error processing text/file: {str(e)}"
            print(error_msg)
            return (input_text,)  # Fallback to input text on error

    def _prepare_filepath(self, filename):
        """Prepare the complete file path with proper directory and extension."""
        # Get input directory
        input_dir = folder_paths.get_input_directory().replace("\\", "/")
        
        # Ensure directory exists
        os.makedirs(input_dir, exist_ok=True)
        
        # Add .txt extension if no extension present
        if not self._has_text_extension(filename):
            filename = filename + ".txt"
        
        return os.path.join(input_dir, filename)

    def _has_text_extension(self, filename):
        """Check if filename has a text-related extension."""
        text_extensions = ['.txt', '.text', '.md', '.markdown']
        return any(filename.lower().endswith(ext) for ext in text_extensions)

    def _load_file_content(self, filepath):
        """
        Load content from file safely.
        
        Args:
            filepath: Path to the file to load
            
        Returns:
            str or None: File content if successful, None if file doesn't exist
        """
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, "r", encoding=self.DEFAULT_ENCODING) as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            try:
                with open(filepath, "r", encoding="latin-1") as file:
                    return file.read()
            except Exception as e:
                print(f"Error reading file with latin-1 encoding: {str(e)}")
                return None
        except Exception as e:
            print(f"Error reading file {filepath}: {str(e)}")
            return None

    def _handle_file_not_found(self, input_text, fallback_mode, filepath):
        """Handle the case when the file doesn't exist."""
        print(f"File not found: {filepath}")
        
        if fallback_mode == "use_input":
            print("Using input text as fallback")
            return (input_text,)
        else:  # empty_string
            print("Using empty string as fallback")
            return ("",)

    def _combine_texts(self, file_content, input_text, action):
        """
        Combine file content and input text based on the specified action.
        
        Args:
            file_content: Content loaded from file
            input_text: User input text
            action: How to combine the texts
            
        Returns:
            str: Combined text result
        """
        if action == "append":
            return file_content + input_text
        elif action == "prepend":
            return input_text + file_content
        elif action == "replace":
            return input_text
        else:
            # Fallback to append if unknown action
            print(f"Unknown action '{action}', using append")
            return file_content + input_text
