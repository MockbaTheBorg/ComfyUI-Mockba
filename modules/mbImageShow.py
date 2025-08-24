"""
mbImageShow - simple image preview node that emits a base64 image for JS display.

This node accepts any input that can be converted to an image (image tensor, mask,
or other types which will be converted to a text image) and returns the image
tensor as output while embedding a PNG base64 string in the UI payload under
`image_show` so a companion frontend script can render it inside the node.
"""
import base64
from io import BytesIO
import json
import numpy as np
import torch
from PIL import Image

from .common import (
    any_typ,
    create_text_image,
    convert_pil_to_tensor,
    is_mask_tensor,
    convert_mask_to_image_enhanced,
    convert_pil_to_tensor,
    tensor_to_pil_image,
)
from .common import CATEGORIES


class mbImageShow:
    """A lightweight image viewer node that sends PNG base64 to the frontend."""

    def __init__(self):
        import uuid
        self._unique_id = str(uuid.uuid4())[:8]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": (any_typ,)
            }
        }

    TITLE = "Image Show"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "show_image"
    CATEGORY = "unset"
    DESCRIPTION = "Send a preview of the input image to the UI (base64 PNG) for inline display."
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        import time
        return time.time()

    def show_image(self, images, title="Image Show"):
        try:
            # Determine if input is a tensor-like image
            is_tensor = hasattr(images, 'shape') and hasattr(images, 'cpu')

            if not is_tensor:
                # Convert other types to a text image for display
                if isinstance(images, (list, tuple)):
                    text_content = "".join([f"Item {i+1}: {str(item)}\n" for i, item in enumerate(images)])
                elif isinstance(images, dict):
                    text_content = "Dictionary contents:\n" + "\n".join([f"{k}: {v}" for k, v in images.items()])
                else:
                    text_content = str(images)

                pil_img = create_text_image(text_content)
                images = convert_pil_to_tensor(pil_img)
            else:
                # If it's a mask-like tensor, convert to an image
                if is_mask_tensor(images):
                    images = convert_mask_to_image_enhanced(images)

            # Ensure batch dimension
            if len(images.shape) == 3:
                images = images.unsqueeze(0)

            # Prepare the first image for display
            pixels = images

            # Use shared conversion utility to produce a PIL image for display
            pil = tensor_to_pil_image(images[0])

            # Encode to PNG base64
            buffer = BytesIO()
            pil.save(buffer, format='PNG')
            buffer.seek(0)
            image_b64 = base64.b64encode(buffer.getvalue()).decode()

            ui_item = {
                'title': title,
                'image_b64': image_b64
            }

            return {"ui": {"image_show": [ui_item]}, "result": (pixels,)}

        except Exception as e:
            print(f"mbImageShow error: {e}")
            # Return a red error image
            try:
                import numpy as _np
                import torch as _torch
                err_h, err_w = 128, 128
                err_img = _np.zeros((err_h, err_w, 3), dtype=_np.uint8)
                err_img[:, :, 0] = 255
                pil = Image.fromarray(err_img, mode='RGB')
                buffer = BytesIO()
                pil.save(buffer, format='PNG')
                b64 = base64.b64encode(buffer.getvalue()).decode()
                ui_item = {'title': 'error', 'image_b64': b64}
                return {"ui": {"image_show": [ui_item]}, "result": (_torch.from_numpy(err_img.astype(_np.float32)/255.0)[None,],)}
            except Exception:
                return {"ui": {"image_show": []}, "result": (torch.zeros((1, 64, 64, 3)),)}
