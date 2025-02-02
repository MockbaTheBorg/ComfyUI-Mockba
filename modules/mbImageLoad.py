import os
import folder_paths
import torch
import numpy as np
import hashlib
from PIL import Image, ImageOps

# Loads an image from a file.
class mbImageLoad:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        input_dir = folder_paths.get_input_directory()
        exclude_folders = ["clipspace"]
        file_list = []
        for root, dirs, files in os.walk(input_dir):
            dirs[:] = [d for d in dirs if d not in exclude_folders]
            for file in files:
                if not file.endswith(".png"):
                    continue
                file_path = os.path.relpath(os.path.join(root, file), start=input_dir)
                file_path = file_path.replace("\\", "/")
                file_list.append(file_path)

        return {
            "required": {"image": (sorted(file_list), {"image_upload": True})},
        }

    RETURN_TYPES = (
        "IMAGE",
        "MASK",
    )
    RETURN_NAMES = (
        "image",
        "mask",
    )
    FUNCTION = "execute"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Loads image with subfolders."

    def execute(self, image):
        image_path = folder_paths.get_annotated_filepath(image)
        i = Image.open(image_path)
        i = ImageOps.exif_transpose(i)
        image = i.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        if "A" in i.getbands():
            mask = np.array(i.getchannel("A")).astype(np.float32) / 255.0
            mask = 1.0 - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
        print("Loaded: " + image_path)
        return (image, mask.unsqueeze(0))

    @classmethod
    def IS_CHANGED(self, image):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, "rb") as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(self, image):
        image_path = folder_paths.get_annotated_filepath(image)
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)
        return True


