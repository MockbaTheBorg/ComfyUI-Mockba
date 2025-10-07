"""
ComfyUI node to select a string from a multi line text input.
The node has no inputs and a single output that returns the selected line.
There is one multi line text fiel for the user to enter lines of text.
There is a dropdown to select if the lines will be selected randomly or sequentially.
The node maintains state to track the last selected line for sequential selection.
When using random selection, the node uses a fixed seed for reproducibility.
When using random selection, the node avoids repeating a previous selection, unless there is only one line.
"""

import random
import json
import os
import hashlib

class mbStringSelector:
    """Node to select a string from multiline text input."""
    
    STATE_FILE = os.path.join(os.path.dirname(__file__), "mbStringSelector_state.json")
    
    def __init__(self):
        """Initialize the string selector node."""
        self.state = self.load_state()
    
    def load_state(self):
        """Load state from file."""
        if os.path.exists(self.STATE_FILE):
            try:
                with open(self.STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_state(self):
        """Save state to file."""
        try:
            with open(self.STATE_FILE, 'w') as f:
                json.dump(self.state, f)
        except:
            pass
    
    def get_text_hash(self, text):
        """Get hash of the text."""
        return hashlib.md5(text.encode()).hexdigest()

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for string selection."""
        return {
            "required": {
                "text": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Multiline text input with lines to select from"
                }),
                "mode": (["random", "sequential"], {
                    "default": "random",
                    "tooltip": "Selection mode: random or sequential"
                }),
            }
        }

    # Node metadata
    TITLE = "String Selector"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("selected_line",)
    FUNCTION = "select_string"
    CATEGORY = "unset"
    DESCRIPTION = "Select a string from multiline text input randomly or sequentially."

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """Force execution every time by returning a unique value."""
        import time
        return time.time()

    def select_string(self, text, mode):
        """
        Select a line from the multiline text based on the mode.
        
        Args:
            text: Multiline text input
            mode: Selection mode ("random" or "sequential")
            
        Returns:
            tuple: Selected line as string
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return ("",)
        
        text_hash = self.get_text_hash(text)
        
        if self.state.get('text_hash') != text_hash:
            # Text changed, reset state
            self.state = {'text_hash': text_hash, 'sequential_index': 0, 'remaining_indices': list(range(len(lines)))}
        
        if mode == "sequential":
            idx = self.state['sequential_index']
            selected = lines[idx]
            self.state['sequential_index'] = (idx + 1) % len(lines)
            self.save_state()
            return (selected,)
        
        elif mode == "random":
            remaining = self.state['remaining_indices']
            if not remaining:
                remaining = list(range(len(lines)))
                self.state['remaining_indices'] = remaining
            
            random.seed(42)  # Fixed seed for reproducibility
            idx = random.choice(remaining)
            selected = lines[idx]
            remaining.remove(idx)
            self.save_state()
            return (selected,)
        
        return ("",)



