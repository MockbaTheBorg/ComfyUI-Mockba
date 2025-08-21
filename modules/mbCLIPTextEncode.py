"""
CLIP Text Encoder Node for ComfyUI
Encodes text prompts using CLIP models for diffusion model guidance.
"""

# ComfyUI imports
from comfy.comfy_types import IO, ComfyNodeABC, InputTypeDict

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
        "Supports dynamic prompts and multiline text input."
    )

    def encode_text(self, clip, text):
        """
        Encode text using CLIP model.
        
        Args:
            clip: CLIP model instance for text encoding
            text: Text prompt to encode
            
        Returns:
            tuple: (conditioning embeddings, original text)
            
        Raises:
            RuntimeError: If CLIP model is invalid or None
        """
        try:
            # Validate CLIP model
            self._validate_clip_model(clip)
            
            # Tokenize and encode text
            conditioning = self._encode_text_with_clip(clip, text)
            
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
