import os
import folder_paths
import gc
import time
import torch
import base64
import hashlib
import numpy as np

import nodes

from PIL import Image, ImageOps
from pprint import pprint

import comfy.sample
import comfy.samplers
import comfy.utils
import comfy.model_management

import latent_preview

MAX_RESOLUTION = 4096


# A proxy class that always returns True when compared to any other object.
class AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False


any_typ = AlwaysEqualProxy("*")


# Creates a batch from an arbitrary number of images
class mbImageBatch:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image1": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "batch_image"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Creates a batch from an arbitrary number of images."

    def batch_image(self, **kwargs):
        image1 = kwargs["image1"]
        del kwargs["image1"]
        images = [value for value in kwargs.values()]

        if len(images) == 0:
            return (image1,)
        else:
            for image2 in images:
                if image1.shape[1:] != image2.shape[1:]:
                    image2 = comfy.utils.common_upscale(
                        image2.movedim(-1, 1),
                        image1.shape[2],
                        image1.shape[1],
                        "lanczos",
                        "center",
                    ).movedim(1, -1)
                image1 = torch.cat((image1, image2), dim=0)
            return (image1,)


# Flips an image horizontally or vertically.
class mbImageFlip:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": ("IMAGE",),
                "flip": (["none", "horizontal", "vertical", "both"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "flip_image"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Flips an image horizontally or vertically."

    def flip_image(self, image, flip):
        if flip == "none":
            return (image,)

        image_np = 255.0 * image.cpu().numpy().squeeze()

        if flip == "horizontal":
            flipped_image_np = np.flip(image_np, axis=1)
        elif flip == "vertical":
            flipped_image_np = np.flip(image_np, axis=0)
        elif flip == "both":
            flipped_image_np = np.flip(np.flip(image_np, axis=1), axis=0)
        else:
            print(
                f"Invalid flip. Must be either 'none', 'horizontal', 'vertical' or 'both'. No changes applied."
            )
            return (image,)

        flipped_image_np = flipped_image_np.astype(np.float32) / 255.0
        flipped_image_tensor = torch.from_numpy(flipped_image_np).unsqueeze(0)

        return (flipped_image_tensor,)


# Rotates an image by 90, 180 or 270 degrees ccw.
class mbImageRot:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": ("IMAGE",),
                "degrees": (["0", "90", "180", "270"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "rotate_image"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Rotates an image by 90, 180 or 270 degrees ccw."

    def rotate_image(self, image, degrees):
        if degrees == "0":
            return (image,)

        # Convert the input image tensor to a NumPy array
        image_np = 255.0 * image.cpu().numpy().squeeze()

        if degrees == "90":
            rotated_image_np = np.rot90(image_np)
        elif degrees == "180":
            rotated_image_np = np.rot90(image_np, 2)
        elif degrees == "270":
            rotated_image_np = np.rot90(image_np, 3)
        else:
            print(
                f"Invalid degrees. Must be either '0', '90', '180' or '270'. No changes applied."
            )
            return (image,)

        # Convert the rotated NumPy array back to a tensor
        rotated_image_np = rotated_image_np.astype(np.float32) / 255.0
        rotated_image_tensor = torch.from_numpy(rotated_image_np).unsqueeze(0)

        return (rotated_image_tensor,)


# Subtracts two images. Used to visually measure the difference between two images.
class mbImageSubtract:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "a": ("IMAGE",),
                "b": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "subtract"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = (
        "Subtracts two images. Used to measure the difference between two images."
    )

    def subtract(self, a, b):
        return (abs(a - b),)


# Converts an image to black and white using dithering
class mbImageDither:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "dither"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Converts an image to black and white using dithering."

    def dither(self, image):
        image_np = 255.0 * image.cpu().numpy().squeeze()
        image_pil = Image.fromarray(image_np.astype(np.uint8))
        image_bw_pil = image_pil.convert("1")
        image_bw_np = np.array(image_bw_pil).astype(np.float32)
        image_bw_tensor = torch.from_numpy(image_bw_np).unsqueeze(0)
        return (image_bw_tensor,)


# Returns the width and height of an image.
class mbImageDimensions:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = (
        "INT",
        "INT",
    )
    RETURN_NAMES = (
        "width",
        "height",
    )
    FUNCTION = "get_size"
    CATEGORY = "🖖 Mockba/tools"
    DESCRIPTION = "Returns the width and height of an image."

    def get_size(self, image):
        image_size = image.size()
        image_width = int(image_size[2])
        image_height = int(image_size[1])
        return (
            image_width,
            image_height,
        )


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
    FUNCTION = "load_image"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Loads image with subfolders."

    def load_image(self, image):
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


# Loads an image from an URL.
class mbImageLoadURL:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {"url": ("STRING", {"default": ""})},
        }

    RETURN_TYPES = (
        "IMAGE",
        "MASK",
    )
    RETURN_NAMES = (
        "image",
        "mask",
    )
    FUNCTION = "load_image_url"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Loads an image from an URL."

    def load_image_url(self, url):
        import requests
        from io import BytesIO

        response = requests.get(url)
        i = Image.open(BytesIO(response.content))
        i = ImageOps.exif_transpose(i)
        image = i.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        if "A" in i.getbands():
            mask = np.array(i.getchannel("A")).astype(np.float32) / 255.0
            mask = 1.0 - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
        return (image, mask.unsqueeze(0))


# Preview bridge
def is_execution_model_version_supported():
    try:
        import comfy_execution
        return True
    except:
        return False
def set_previewbridge_image(node_id, file, item):
    global pb_id_cnt

    if file in preview_bridge_image_name_map:
        pb_id = preview_bridge_image_name_map[node_id, file]
        if pb_id.startswith(f"${node_id}"):
            return pb_id

    pb_id = f"${node_id}-{pb_id_cnt}"
    preview_bridge_image_id_map[pb_id] = (file, item)
    preview_bridge_image_name_map[node_id, file] = (pb_id, item)
    if os.path.isfile(file):
        i = Image.open(file)
        i = ImageOps.exif_transpose(i)
        if 'A' in i.getbands():
            mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)
            preview_bridge_last_mask_cache[node_id] = mask.unsqueeze(0)
    pb_id_cnt += 1

    return pb_id
pb_id_cnt = time.time()
preview_bridge_image_id_map = {}
preview_bridge_image_name_map = {}
preview_bridge_cache = {}
preview_bridge_last_mask_cache = {}
class mbPreviewBridge:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {"required": {
                    "images": ("IMAGE",),
                    "image": ("STRING", {"default": ""}),
                    },
                "optional": {
                    "block": ("BOOLEAN", {"default": False, "label_on": "if_empty_mask", "label_off": "never", "tooltip": "is_empty_mask: If the mask is empty, the execution is stopped.\nnever: The execution is never stopped."}),
                    "restore_mask": (["never", "always", "if_same_size"], {"tooltip": "if_same_size: If the changed input image is the same size as the previous image, restore using the last saved mask\nalways: Whenever the input image changes, always restore using the last saved mask\nnever: Do not restore the mask.\n`restore_mask` has higher priority than `block`"}),
                    },
                "hidden": {"unique_id": "UNIQUE_ID", "extra_pnginfo": "EXTRA_PNGINFO"},
                }

    RETURN_TYPES = (
        "IMAGE",
        "MASK",
    )
    RETURN_NAMES = (
        "image",
        "mask",
    )
    FUNCTION = "preview_bridge"
    CATEGORY = "🖖 Mockba/image"
    DESCRIPTION = "Previews and forwards an image."
    OUTPUT_NODE = True

    def __init__(self):
        super().__init__()
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prev_hash = None

    @staticmethod
    def load_image(pb_id):
        is_fail = False
        if pb_id not in preview_bridge_image_id_map:
            is_fail = True

        image_path, ui_item = preview_bridge_image_id_map[pb_id]

        if not os.path.isfile(image_path):
            is_fail = True

        if not is_fail:
            i = Image.open(image_path)
            i = ImageOps.exif_transpose(i)
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]

            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
        else:
            image = empty_pil_tensor()
            mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
            ui_item = {
                "filename": 'empty.png',
                "subfolder": '',
                "type": 'temp'
            }

        return image, mask.unsqueeze(0), ui_item

    def preview_bridge(self, images, image, unique_id, block=False, restore_mask="never", prompt=None, extra_pnginfo=None):
        need_refresh = False

        if unique_id not in preview_bridge_cache:
            need_refresh = True

        elif preview_bridge_cache[unique_id][0] is not images:
            need_refresh = True

        if not need_refresh:
            pixels, mask, path_item = mbPreviewBridge.load_image(image)
            image = [path_item]
        else:
            if restore_mask != "never":
                mask = preview_bridge_last_mask_cache.get(unique_id)
                if mask is None or (restore_mask != "always" and mask.shape[1:] != images.shape[1:3]):
                    mask = None
            else:
                mask = None

            if mask is None:
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
                res = nodes.PreviewImage().save_images(images, filename_prefix="PreviewBridge/PB-", prompt=prompt, extra_pnginfo=extra_pnginfo)
            else:
                masked_images = tensor_convert_rgba(images)
                resized_mask = resize_mask(mask, (images.shape[1], images.shape[2])).unsqueeze(3)
                resized_mask = 1 - resized_mask
                tensor_putalpha(masked_images, resized_mask)
                res = nodes.PreviewImage().save_images(masked_images, filename_prefix="PreviewBridge/PB-", prompt=prompt, extra_pnginfo=extra_pnginfo)

            image2 = res['ui']['images']
            pixels = images

            path = os.path.join(folder_paths.get_temp_directory(), 'PreviewBridge', image2[0]['filename'])
            set_previewbridge_image(unique_id, path, image2[0])
            preview_bridge_image_id_map[image] = (path, image2[0])
            preview_bridge_image_name_map[unique_id, path] = (image, image2[0])
            preview_bridge_cache[unique_id] = (images, image2)

            image = image2

        is_empty_mask = torch.all(mask == 0)

        if block and is_empty_mask and is_execution_model_version_supported():
            from comfy_execution.graph import ExecutionBlocker
            result = ExecutionBlocker(None), ExecutionBlocker(None)
        elif block and is_empty_mask:
            print(f"MockbaPreviewBridge: ComfyUI is outdated - blocking feature is disabled.")
            result = pixels, mask
        else:
            result = pixels, mask

        if not is_empty_mask:
            preview_bridge_last_mask_cache[unique_id] = mask

        return {
            "ui": {"images": image},
            "result": result,
        }

    
# Select an output from an arbitrary number of inputs
class mbSelect:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "select": ("INT", {"default": 1, "min": 1, "max": 100, "step": 1}),
            },
            "optional": {
                "input1": (any_typ,),
            },
            "hidden": {"unique_id": "UNIQUE_ID", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("out",)
    FUNCTION = "select"
    CATEGORY = "🖖 Mockba/tools"
    DESCRIPTION = "Select an output from an arbitrary number of inputs."

    def select(self, *args, **kwargs):
        selected_index = int(kwargs["select"])
        input_name = f"input{selected_index}"

        if input_name in kwargs:
            return (kwargs[input_name],)
        else:
            print(f"mb Select: invalid selection (ignored)")
            return (None,)


# Functions
def mask_to_image(mask):
    result = mask.reshape((-1, 1, mask.shape[-2], mask.shape[-1])).movedim(1, -1).expand(-1, -1, -1, 3)
    return result

# Evaluate a python expression on inputs and return the result.
class mbEval:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "code": ("STRING", {"default": ""}),
            },
            "optional": {
                "i1": (any_typ,),
            }
        }

    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("out",)
    FUNCTION = "eval"
    CATEGORY = "🖖 Mockba/tools"
    DESCRIPTION = "Evaluate a python expression on inputs and return the result."

    def eval(self, code, *args, **kwargs):
        for key, value in kwargs.items():
            exec(f"{key} = value")
        if code == "":
            code = "i1"
        return (eval(code),)


# Execute python code on inputs and return the result.
class mbExec:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "code": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "i1": (any_typ,),
            }
        }

    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("out",)
    FUNCTION = "exec"
    CATEGORY = "🖖 Mockba/tools"
    DESCRIPTION = "Evaluate a python expression on inputs and return the result."

    def exec(self, code, *args, **kwargs):
        out = None
        if code == "":
            code = "out = i1"
        globals = {}
        for key, value in kwargs.items():
            globals[key] = value
        locals = {}
        exec(code, globals, locals)
        if "out" in locals:
            out = locals["out"]
        return (out,)


# Saves an image to a file.
class mbImageToFile:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": ("IMAGE",),
                "base_name": ("STRING", {"default": "image"}),
                "id": ("INT", {"default": 0, "min": 0, "step": 1}),
                "use_id": (["yes", "no"], {"default": "no"}),
            },
        }

    RETURN_TYPES = (
        "IMAGE",
        "INT",
    )
    RETURN_NAMES = (
        "image",
        "id",
    )
    FUNCTION = "mbImageSave"
    CATEGORY = "🖖 Mockba/file"
    DESCRIPTION = "Saves an image to a file."

    def mbImageSave(self, image, base_name, id, use_id):
        prefix = folder_paths.get_input_directory()
        if not os.path.exists(prefix):
            os.makedirs(prefix)
        if use_id == "yes":
            filename = base_name + "_" + str(id) + ".png"
        else:
            filename = base_name + ".png"
        image_np = 255.0 * image.cpu().numpy().squeeze()
        image_pil = Image.fromarray(image_np.astype(np.uint8))
        image_pil.save(prefix + filename)
        return (
            image,
            id,
        )


# Loads an image from a file.
class mbFileToImage:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "base_name": ("STRING", {"default": "image"}),
                "id": ("INT", {"default": 0, "min": 0, "step": 1}),
                "use_id": (["yes", "no"], {"default": "no"}),
            }
        }

    RETURN_TYPES = (
        "IMAGE",
        "INT",
    )
    RETURN_NAMES = (
        "image",
        "id",
    )
    FUNCTION = "mbImageLoad"
    CATEGORY = "🖖 Mockba/file"
    DESCRIPTION = "Loads an image from a file."

    def mbImageLoad(self, base_name, id, use_id):
        prefix = folder_paths.get_input_directory()
        if use_id == "yes":
            filename = base_name + "_" + str(id) + ".png"
        else:
            filename = base_name + ".png"
        if not os.path.exists(prefix + filename):
            return (torch.zeros([1, 512, 512, 3]),)
        image_pil = Image.open(prefix + filename)
        image_np = np.array(image_pil).astype(np.float32) / 255.0
        image = torch.from_numpy(image_np).unsqueeze(0)
        return (
            image,
            id,
        )


# Saves text to a file.
class mbTextToFile:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "text": ("STRING", {"default": "text"}),
                "base_name": ("STRING", {"default": "text"}),
                "id": ("INT", {"default": 0, "min": 0, "step": 1}),
                "use_id": (["yes", "no"], {"default": "no"}),
            },
        }

    RETURN_TYPES = (
        "STRING",
        "INT",
    )
    RETURN_NAMES = (
        "text",
        "id",
    )
    FUNCTION = "mbTextSave"
    CATEGORY = "🖖 Mockba/file"
    DESCRIPTION = "Saves text to a file."

    def mbTextSave(self, text, base_name, id, use_id):
        prefix = folder_paths.get_input_directory()
        if not os.path.exists(prefix):
            os.makedirs(prefix)
        if use_id == "yes":
            filename = base_name + "_" + str(id) + ".txt"
        else:
            filename = base_name + ".txt"
        with open(prefix + filename, "w") as f:
            f.write(text)
        return (
            text,
            id,
        )


# Loads text from a file.
class mbFileToText:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "default": ("STRING", {"default": ""}),
                "base_name": ("STRING", {"default": "text"}),
                "id": ("INT", {"default": 0, "min": 0, "step": 1}),
                "use_id": (["yes", "no"], {"default": "no"}),
            }
        }

    RETURN_TYPES = (
        "STRING",
        "INT",
    )
    RETURN_NAMES = (
        "text",
        "id",
    )
    FUNCTION = "mbTextLoad"
    CATEGORY = "🖖 Mockba/file"
    DESCRIPTION = "Loads text from a file."

    def mbTextLoad(self, default, base_name, id, use_id):
        if default != "":
            return (default, id)
        prefix = folder_paths.get_input_directory()
        if use_id == "yes":
            filename = base_name + "_" + str(id) + ".txt"
        else:
            filename = base_name + ".txt"
        if not os.path.exists(prefix + filename):
            return ("",)
        with open(prefix + filename, "r") as f:
            text = f.read()
        return (
            text,
            id,
        )


# loads text from a file or uses the entered value.
class mbTextOrFile:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "input": ("STRING", {"default": "", "multiline": True}),
                "base_name": ("STRING", {"default": "filename"}),
                "action": (["append", "prepend", "replace"], {"default": "append"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "mbTextOrFile"
    CATEGORY = "🖖 Mockba/file"
    DESCRIPTION = "Loads text from a file or uses the entered value."

    def mbTextOrFile(self, input, base_name, action):
        prefix = folder_paths.get_input_directory()
        if not os.path.exists(prefix):
            os.makedirs(prefix)
        filename = base_name + ".txt"
        if not os.path.exists(prefix + filename):
            return (input,)
        with open(prefix + filename, "r") as f:
            file_text = f.read()
        if action == "append":
            file_text = file_text + input
        elif action == "prepend":
            file_text = input + file_text
        elif action == "replace":
            file_text = input
        return (file_text,)


# Shows debug information about the input object.
class mbDebug:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "input": (any_typ, {}),
                "element": ("STRING", {"default": "element name"}),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "debug"
    CATEGORY = "🖖 Mockba/tools"
    DESCRIPTION = "Shows debug information about the input object."
    OUTPUT_NODE = True

    def debug(self, input, element):

        print(f"Debug {element}:")
        if isinstance(input, object) and not isinstance(
            input, (str, int, float, bool, list, dict, tuple)
        ):
            print("Objects directory listing:")
            pprint(dir(input), indent=4)
        else:
            print(input)

        return ()


# Creates an empty latent image using the cpu or gpu.
class mbEmptyLatentImage:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        devices = ["cpu", "cuda"]
        default_device = devices[0]

        resolutions = []
        with open("ComfyUI/custom_nodes/ComfyUI-Mockba/resolutions.txt", "r") as f:
            for line in f:
                resolutions.append(line.strip())
        default_resolution = resolutions[0]

        return {
            "required": {
                "size": (
                    resolutions,
                    {"default": default_resolution},
                ),
                "width": (
                    "INT",
                    {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8},
                ),
                "height": (
                    "INT",
                    {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8},
                ),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64}),
                "device": (devices, {"default": default_device}),
                "garbage_collect": (
                    "BOOLEAN",
                    {"default": False, "label_on": "enable", "label_off": "disable"},
                ),
            }
        }

    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent_image",)
    FUNCTION = "generate"
    CATEGORY = "🖖 Mockba"
    DESCRIPTION = "Creates an empty latent image using the cpu or gpu."

    def generate(self, size, width, height, batch_size, device, garbage_collect):
        if garbage_collect:
            gc.collect()
            if device.startswith("cuda"):
                torch.cuda.ipc_collect()
                torch.cuda.empty_cache()

        if size == "------":
            size = "custom"
        if size == "custom":
            n_width = width
            n_height = height
        else:
            n_width = int(size.split("x")[0])
            n_height = int(size.split("x")[1])

        latent = torch.zeros(
            [batch_size, 4, n_height // 8, n_width // 8], device=device
        )
        return (
            {
                "samples": latent,
            },
        )


# creates random noise given a latent image and a seed.
def my_prepare_noise(latent_image, seed, noise_inds=None):
    generator = torch.Generator(device=latent_image.device)
    generator.manual_seed(seed)
    if noise_inds is None:
        noise = torch.randn(
            latent_image.size(),
            dtype=latent_image.dtype,
            layout=latent_image.layout,
            generator=generator,
            device=latent_image.device,
        )
        return noise

    unique_inds, inverse = np.unique(noise_inds, return_inverse=True)
    noises = []
    for i in range(unique_inds[-1] + 1):
        noise = torch.randn(
            [1] + list(latent_image.size())[1:],
            dtype=latent_image.dtype,
            layout=latent_image.layout,
            generator=generator,
            device=latent_image.device,
        )
        if i in unique_inds:
            noises.append(noise)
    noises = [noises[i] for i in inverse]
    noises = torch.cat(noises, axis=0)
    return (noises,)


# Runs a model with a given latent image using cpu or gpu and returns the resulting latent image.
def my_common_ksampler(
    model,
    seed,
    steps,
    cfg,
    sampler_name,
    scheduler,
    positive,
    negative,
    latent,
    denoise=1.0,
    disable_noise=False,
    start_step=None,
    last_step=None,
    force_full_denoise=False,
):
    latent_image = latent["samples"]

    if disable_noise:
        noise = torch.zeros(
            latent_image.size(),
            dtype=latent_image.dtype,
            layout=latent_image.layout,
            device=latent.device,
        )
    else:
        batch_inds = latent["batch_index"] if "batch_index" in latent else None
        noise = my_prepare_noise(latent_image, seed, batch_inds)

    noise_mask = None
    if "noise_mask" in latent:
        noise_mask = latent["noise_mask"]

    callback = latent_preview.prepare_callback(model, steps)
    disable_pbar = not comfy.utils.PROGRESS_BAR_ENABLED
    samples = comfy.sample.sample(
        model,
        noise,
        steps,
        cfg,
        sampler_name,
        scheduler,
        positive,
        negative,
        latent_image,
        denoise=denoise,
        disable_noise=disable_noise,
        start_step=start_step,
        last_step=last_step,
        force_full_denoise=force_full_denoise,
        noise_mask=noise_mask,
        callback=callback,
        disable_pbar=disable_pbar,
        seed=seed,
    )
    out = latent.copy()
    out["samples"] = samples
    return (out,)


# Runs a model with a given latent image using cpu or gpu and returns the resulting latent image.
class mbKSampler:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "model": ("MODEL",),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
                "latent_image": ("LATENT",),
                "denoise": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent_image",)
    FUNCTION = "sample"
    CATEGORY = "🖖 Mockba"
    DESCRIPTION = "Runs a model with a given latent image using cpu or gpu and returns the resulting latent image."

    def sample(
        self,
        model,
        seed,
        steps,
        cfg,
        sampler_name,
        scheduler,
        positive,
        negative,
        latent_image,
        denoise=1.0,
    ):
        return my_common_ksampler(
            model,
            seed,
            steps,
            cfg,
            sampler_name,
            scheduler,
            positive,
            negative,
            latent_image,
            denoise=denoise,
        )


# Runs a model with a given latent image using cpu or gpu and returns the resulting latent image (advanced).
class mbKSamplerAdvanced:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "model": ("MODEL",),
                "add_noise": (["enable", "disable"],),
                "noise_seed": (
                    "INT",
                    {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF},
                ),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
                "latent_image": ("LATENT",),
                "start_at_step": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "end_at_step": ("INT", {"default": 10000, "min": 0, "max": 10000}),
                "return_with_leftover_noise": (["disable", "enable"],),
            }
        }

    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent_image",)
    FUNCTION = "sample"
    CATEGORY = "🖖 Mockba"
    DESCRIPTION = "Runs a model with a given latent image using cpu or gpu and returns the resulting latent image."

    def sample(
        self,
        model,
        add_noise,
        noise_seed,
        steps,
        cfg,
        sampler_name,
        scheduler,
        positive,
        negative,
        latent_image,
        start_at_step,
        end_at_step,
        return_with_leftover_noise,
        denoise=1.0,
    ):
        force_full_denoise = True
        if return_with_leftover_noise == "enable":
            force_full_denoise = False
        disable_noise = False
        if add_noise == "disable":
            disable_noise = True
        return my_common_ksampler(
            model,
            noise_seed,
            steps,
            cfg,
            sampler_name,
            scheduler,
            positive,
            negative,
            latent_image,
            denoise=denoise,
            disable_noise=disable_noise,
            start_step=start_at_step,
            last_step=end_at_step,
            force_full_denoise=force_full_denoise,
        )


# Generates a hash given a seed and a base string.
class mbHashGenerator:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "seed": ("STRING", {"default": "000000000000"}),
                "base_string": ("STRING", {"default": "text"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("hash",)
    FUNCTION = "mbHashGenerate"
    CATEGORY = "🖖 Mockba/tools"
    DESCRIPTION = "Generates a hash given a seed and a base string."

    def mbHashGenerate(self, seed, base_string):
        mac = seed.replace(":", "")
        dic = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        data = base64.b64decode("R2FyeQ==").decode("utf-8")
        data += mac
        data += base64.b64decode("bWFzdGVy").decode("utf-8")
        data += base_string
        md = hashlib.sha1(data.encode("utf-8")).digest()
        v = []
        for i in range(8):
            k = i + 8 + (i < 4) * 8
            v.append(md[i] ^ md[k])

        pw = ""
        for i in range(8):
            pw += dic[v[i] + 2 * (v[i] // 62) - ((v[i] // 62) << 6)]

        return (base_string + "-" + pw,)


# Returns a multiline string text.
class mbText:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "mbText"
    CATEGORY = "🖖 Mockba/tools"
    DESCRIPTION = "Returns a multiline string text."

    def mbText(self, text):
        return (text,)


# Returns a single line string text.
class msString:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "text": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "mbString"
    CATEGORY = "🖖 Mockba/tools"
    DESCRIPTION = "Returns a single line string text."

    def mbString(self, text):
        return (text,)
