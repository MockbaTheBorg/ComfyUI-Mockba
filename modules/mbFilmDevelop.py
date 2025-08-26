"""
Film Develop Node for ComfyUI
Converts color film negatives into developed positives with adjustable controls
for exposure, contrast, saturation, per-channel gains, gamma and auto white balance.
"""

import torch
import numpy as np
from PIL import Image, ImageEnhance


class mbFilmDevelop:
    """Develop a film negative image (color negative) into a positive image.
    This node performs an inversion plus color-cast correction and tone adjustments.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "Input film negative image tensor (0..1)"}),
            },
            "optional": {
                "exposure": ("FLOAT", {"default": 0.0, "min": -2.0, "max": 2.0, "step": 0.01, "tooltip": "Stops of exposure (+ brighten / - darken)"}),
                "contrast": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.01, "tooltip": "Contrast multiplier"}),
                "saturation": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.01, "tooltip": "Color saturation multiplier"}),
                "red_gain": ("FLOAT", {"default": 1.0, "min": 0.2, "max": 3.0, "step": 0.01, "tooltip": "Red channel gain (color balance)"}),
                "green_gain": ("FLOAT", {"default": 1.0, "min": 0.2, "max": 3.0, "step": 0.01, "tooltip": "Green channel gain (color balance)"}),
                "blue_gain": ("FLOAT", {"default": 1.0, "min": 0.2, "max": 3.0, "step": 0.01, "tooltip": "Blue channel gain (color balance)"}),
                "gamma": ("FLOAT", {"default": 1.0, "min": 0.3, "max": 3.0, "step": 0.01, "tooltip": "Gamma correction (1 = linear)"}),
                "auto_balance": ("BOOLEAN", {"default": False, "tooltip": "Attempt an automatic neutralization of color cast before manual gains"}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.1, "tooltip": "Mix between simple invert and full developed result (1 = full develop)"}),
            }
        }

    TITLE = "Film Develop"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "develop"
    CATEGORY = "unset"
    DESCRIPTION = "Convert a color film negative into a developed positive with adjustable controls."

    def develop(self, image, exposure=0.0, contrast=1.0, saturation=1.0,
                red_gain=1.0, green_gain=1.0, blue_gain=1.0,
                gamma=1.0, auto_balance=True, strength=1.0):
        """
        Args:
            image: torch tensor [B, H, W, C] with values in [0,1]
            exposure: stops to apply (float)
            contrast: multiplier for contrast via PIL enhancer
            saturation: color saturation multiplier via PIL enhancer
            red/green/blue_gain: per-channel multipliers applied after auto-balance
            gamma: gamma correction (>0)
            auto_balance: whether to apply a simple gray-world balance before gains
            strength: blend between naive invert and the processed result

        Returns:
            tuple: (developed_image_tensor,)
        """
        try:
            # Basic validation and cleanup
            if torch.any(torch.isnan(image)) or torch.any(torch.isinf(image)):
                image = torch.nan_to_num(image, nan=0.0, posinf=1.0, neginf=0.0)

            image = torch.clamp(image, 0.0, 1.0)

            processed_images = []

            for i in range(image.shape[0]):
                img_np = (image[i].cpu().numpy() * 255.0).astype(np.uint8)

                # Ensure 3-channel image
                if img_np.ndim == 2:
                    img_np = np.stack([img_np] * 3, axis=-1)
                elif img_np.shape[2] == 1:
                    img_np = np.concatenate([img_np] * 3, axis=2)

                # Convert to float [0,1]
                img = img_np.astype(np.float32) / 255.0

                # Naive invert (negative -> positive)
                inv = 1.0 - img

                # Auto white balance (gray-world) - optional
                if auto_balance:
                    # avoid division by zero
                    means = inv.reshape(-1, 3).mean(axis=0)
                    avg = means.mean() if means.mean() > 1e-6 else 1.0
                    balance_gains = avg / (means + 1e-6)
                    inv = inv * balance_gains[np.newaxis, np.newaxis, :]

                # Apply manual channel gains (user control)
                channel_gains = np.array([red_gain, green_gain, blue_gain], dtype=np.float32)
                inv = inv * channel_gains[np.newaxis, np.newaxis, :]

                # Exposure (stops): multiply by 2**exposure
                try:
                    inv = inv * (2.0 ** float(exposure))
                except Exception:
                    pass

                # Clip before enhancement
                inv = np.clip(inv, 0.0, 1.0)

                # Convert to PIL for contrast/saturation
                pil = Image.fromarray((inv * 255.0).astype(np.uint8))

                if contrast != 1.0 and contrast > 0.0:
                    enhancer = ImageEnhance.Contrast(pil)
                    pil = enhancer.enhance(float(contrast))

                if saturation != 1.0 and saturation >= 0.0:
                    enhancer = ImageEnhance.Color(pil)
                    pil = enhancer.enhance(float(saturation))

                # Convert back to numpy float
                proc = np.array(pil).astype(np.float32) / 255.0

                # Gamma correction (avoid zero)
                if gamma is None or gamma <= 0:
                    gamma = 1.0
                proc = np.clip(proc, 1e-6, 1.0)
                proc = np.power(proc, 1.0 / float(gamma))

                # Mix with simple invert according to strength
                strength = float(np.clip(strength, 0.0, 1.0))
                result = proc * strength + (1.0 - strength) * (1.0 - img)

                result = np.clip(result, 0.0, 1.0)

                # Convert to tensor and append
                res_t = torch.from_numpy(result.astype(np.float32))
                processed_images.append(res_t)

            out = torch.stack(processed_images, dim=0).to(image.device)
            return (out,)

        except Exception as e:
            print(f"mbFilmDevelop error: {e}")
            # Fallback to simple invert
            fallback = 1.0 - image
            return (fallback,)

