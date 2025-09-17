"""
CLIP Text Encoder Node for ComfyUI
Encodes text prompts using CLIP models for diffusion model guidance.
"""

# ComfyUI imports
from comfy.comfy_types import IO, ComfyNodeABC, InputTypeDict

# Additional imports for caching
import hashlib
import os
import pickle

class mbCLIPTextEncode(ComfyNodeABC):
    """Encode text prompts using CLIP models for diffusion guidance."""
    
    # Class constants
    DEFAULT_TEXT = ""
    
    @classmethod
    def INPUT_TYPES(cls) -> InputTypeDict:
        """Define input types for CLIP text encoding."""
        return {
            "required": {
                "text": (IO.STRING, {
                    "multiline": True, 
                    "dynamicPrompts": True, 
                    "tooltip": "Text prompt to encode using CLIP model"
                }),
                "clip": (IO.CLIP, {
                    "tooltip": "CLIP model for encoding text into embeddings"
                }),
                "cache": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable caching of CLIP encodings to speed up repeated encodings"
                })
            }
        }
    
    # Node metadata
    TITLE = "CLIP Text Encoder"
    RETURN_TYPES = (IO.CONDITIONING, "STRING")
    RETURN_NAMES = ("prompt", "text")
    FUNCTION = "encode_text"
    CATEGORY = "unset"
    DESCRIPTION = (
        "Encode text prompts using CLIP models into embeddings for guiding diffusion model image generation. "
        "Supports dynamic prompts and multiline text input. Includes caching to avoid recomputing identical encodings."
    )

    def encode_text(self, clip, text, cache):
        """
        Encode text using CLIP model, with optional caching.
        
        Args:
            clip: CLIP model instance for text encoding
            text: Text prompt to encode
            cache: Boolean flag to enable/disable caching
            
        Returns:
            tuple: (conditioning embeddings, original text)
            
        Raises:
            RuntimeError: If CLIP model is invalid or None
        """
        try:
            # Validate CLIP model
            self._validate_clip_model(clip)
            
            if cache:
                # Compute 32-bit hash (using MD5, which is 128-bit but we'll take first 8 hex chars for 32-bit representation)
                hash_obj = hashlib.md5(text.encode('utf-8'))
                hash_hex = hash_obj.hexdigest()[:8]  # Take first 8 hex chars (32 bits)
                
                # Define cache directory relative to this module's directory
                cache_dir = os.path.join(os.path.dirname(__file__), '..', 'cache')
                cache_file = os.path.join(cache_dir, f"{hash_hex}.clip")
                
                if os.path.exists(cache_file):
                    # Load from cache
                    with open(cache_file, 'rb') as f:
                        conditioning = pickle.load(f)
                    print(f"Loaded CLIP encoding from cache: {cache_file}")
                    return (conditioning, text)
                else:
                    # Encode and cache
                    conditioning = self._encode_text_with_clip(clip, text)
                    
                    # Ensure cache directory exists
                    os.makedirs(cache_dir, exist_ok=True)
                    
                    # Save to cache
                    with open(cache_file, 'wb') as f:
                        pickle.dump(conditioning, f)
                    print(f"Saved CLIP encoding to cache: {cache_file}")
                    # Save the text to a .txt file
                    txt_file = cache_file.replace('.clip', '.txt')
                    with open(txt_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    return (conditioning, text)
            else:
                # No caching, encode directly
                conditioning = self._encode_text_with_clip(clip, text)
                print("CLIP encoding computed without caching.")
                return (conditioning, text)
            
        except Exception as e:
            error_msg = f"Failed to encode text with CLIP: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)

    def _validate_clip_model(self, clip):
        """Validate that CLIP model is available and valid."""
        if clip is None:
            raise RuntimeError(
                "ERROR: CLIP input is invalid: None\n\n"
                "If the CLIP is from a checkpoint loader node, your checkpoint does not contain "
                "a valid CLIP or text encoder model."
            )

    def _encode_text_with_clip(self, clip, text):
        """Encode text using the CLIP model with proper tokenization."""
        # Tokenize the input text
        tokens = clip.tokenize(text)
        
        # Encode tokens into conditioning embeddings
        conditioning = clip.encode_from_tokens_scheduled(tokens)
        
        return conditioning
