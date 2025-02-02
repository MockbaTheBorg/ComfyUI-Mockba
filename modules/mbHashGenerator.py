import base64
import hashlib

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
