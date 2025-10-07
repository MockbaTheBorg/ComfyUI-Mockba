"""
ComfyUI node to load face models from reactor face models folder.
"""

import os
import glob
from typing import List

# We intentionally avoid importing reactor_utils or nodes.py; reimplement minimal helpers here.

# Determine reactor face models path from ComfyUI's folder_paths module if available, otherwise try env var
try:
    import folder_paths
    models_dir = folder_paths.models_dir
except Exception:
    models_dir = os.path.join(os.path.expanduser("~"), ".cache", "comfyui", "models")

REACTOR_MODELS_PATH = os.path.join(models_dir, "reactor")
FACE_MODELS_PATH = os.path.join(REACTOR_MODELS_PATH, "faces")


def _get_facemodels_recursive() -> List[str]:
    """Return list of .safetensors files under FACE_MODELS_PATH and subdirectories."""
    pattern = os.path.join(FACE_MODELS_PATH, "**", "*.safetensors")
    files = glob.glob(pattern, recursive=True)
    files = [f for f in files if os.path.isfile(f) and f.lower().endswith(".safetensors")]
    files.sort(key=lambda x: os.path.basename(x).lower())
    return files


def _get_model_names() -> dict:
    models = _get_facemodels_recursive()
    names = {}
    for full in models:
        # create a display name that includes subfolder relative path to avoid collisions
        try:
            rel = os.path.relpath(full, FACE_MODELS_PATH)
        except Exception:
            rel = os.path.basename(full)
        # Normalize path separator to forward slash for UI consistency
        rel = rel.replace('\\', '/')
        names[rel] = full
    # keep compatibility with original nodes: include a 'none' option at the top
    ordered = {"none": None}
    for k in sorted(names.keys(), key=str.lower):
        ordered[k] = names[k]
    return ordered


class mbFaceLoad:
    """ComfyUI node that loads a face model from reactor face models folder recursively."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"face_model": (list(_get_model_names().keys()), )}}

    # Node metadata
    TITLE = "Face Model Loader"
    RETURN_TYPES = ("FACE_MODEL",)
    RETURN_NAMES = ("face_model",)
    FUNCTION = "load_model"
    CATEGORY = "unset"
    DESCRIPTION = "Load a face model from the reactor face models folder."

    def load_model(self, face_model):
        if face_model == "none" or face_model is None:
            return (None,)
        # Resolve full path from the mapping (display name -> full path)
        mapping = _get_model_names()
        match = mapping.get(face_model)
        if match is None:
            # fallback: if user provided a basename, try to find it among recursive results
            for p in _get_facemodels_recursive():
                if os.path.basename(p) == face_model:
                    match = p
                    break
        if match is None:
            # final fallback to direct join
            match = os.path.join(FACE_MODELS_PATH, face_model)
        if not os.path.isfile(match):
            # Return None if not found
            return (None,)
        try:
            # Lazy import heavy dependencies to avoid import-time failures
            from safetensors import safe_open
            from insightface.app.common import Face

            # Read tensors using safetensors' safe_open
            data = {}
            with safe_open(match, framework="pt") as f:
                for k in f.keys():
                    data[k] = f.get_tensor(k).numpy()
            face = Face(data)
            return (face,)
        except Exception:
            return (None,)
