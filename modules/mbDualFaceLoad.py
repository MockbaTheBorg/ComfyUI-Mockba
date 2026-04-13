"""
ComfyUI node to load and blend two face models from the reactor face models folder.
"""

import numpy as np

from .mbFaceLoad import _get_model_names, _load_face_tensor_data, load_face_model


def _blend_face_tensor_data(data_a, data_b, balance):
    if data_a is None:
        return data_b
    if data_b is None:
        return data_a

    weight_b = float(balance)
    weight_a = 1.0 - weight_b
    blended = {}

    for key in sorted(set(data_a.keys()) | set(data_b.keys())):
        value_a = data_a.get(key)
        value_b = data_b.get(key)

        if value_a is None:
            blended[key] = np.array(value_b, copy=True)
            continue
        if value_b is None:
            blended[key] = np.array(value_a, copy=True)
            continue

        if getattr(value_a, "shape", None) != getattr(value_b, "shape", None):
            source = value_a if weight_a >= weight_b else value_b
            blended[key] = np.array(source, copy=True)
            continue

        blended[key] = (
            value_a.astype(np.float32) * weight_a
            + value_b.astype(np.float32) * weight_b
        ).astype(np.float32)

    return blended


class mbDualFaceLoad:
    """ComfyUI node that loads two face models and blends their tensors."""

    @classmethod
    def INPUT_TYPES(cls):
        model_names = list(_get_model_names().keys())
        return {
            "required": {
                "face_model_1": (model_names,),
                "face_model_2": (model_names,),
                "balance": (
                    "FLOAT",
                    {
                        "default": 0.5,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.01,
                        "tooltip": "0.0 returns model 1, 1.0 returns model 2, intermediate values blend both.",
                    },
                ),
            }
        }

    TITLE = "Dual Face Model Loader"
    RETURN_TYPES = ("FACE_MODEL",)
    RETURN_NAMES = ("face_model",)
    FUNCTION = "load_model"
    CATEGORY = "unset"
    DESCRIPTION = "Load two reactor face models and blend them with a balance slider."

    def load_model(self, face_model_1, face_model_2, balance):
        try:
            balance = max(0.0, min(1.0, float(balance)))

            if balance <= 0.0:
                return (load_face_model(face_model_1),)
            if balance >= 1.0:
                return (load_face_model(face_model_2),)

            data_a = _load_face_tensor_data(face_model_1)
            data_b = _load_face_tensor_data(face_model_2)
            blended_data = _blend_face_tensor_data(data_a, data_b, balance)

            if blended_data is None:
                return (None,)

            from insightface.app.common import Face

            return (Face(blended_data),)
        except Exception:
            return (None,)