"""
Random Number Node for ComfyUI
Generates integers or floats between Min and Max. If either Min or Max contains a decimal point ('.'),
the node produces floats; otherwise it produces integers. Supports simple distribution selector: 'uniform' or 'normal'.
"""

# Local imports
from .common import any_typ

# Standard library
import random

class mbRandom:
    """Generate random numbers (int or float) based on Min/Max inputs and distribution."""

    def __init__(self):
        """Initialize the random node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for the random node.

        Min and Max are strings so the presence of a decimal point can be detected.
        """
        return {
            "required": {
                "min_value": ("STRING", {
                    "default": "0",
                    "tooltip": "Minimum value. Include a decimal point to force float output (e.g. 0.0)"
                }),
                "max_value": ("STRING", {
                    "default": "1",
                    "tooltip": "Maximum value. Include a decimal point to force float output (e.g. 10.0)"
                }),
                "distribution": (["uniform", "normal"], {
                    "default": "uniform",
                    "tooltip": "Sampling distribution: 'uniform' or 'normal' (Gaussian)"
                }),
            }
        }

    # Node metadata
    TITLE = "Random Number"
    RETURN_TYPES = (any_typ,)
    RETURN_NAMES = ("value",)
    FUNCTION = "generate"
    CATEGORY = "unset"
    DESCRIPTION = (
        "Generate a random number between Min and Max. If either field contains a decimal point, "
        "a float will be produced; otherwise an integer is returned. Supports 'uniform' and 'normal' distributions."
    )

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """Force execution every time by returning a unique value."""
        import time
        return time.time()

    def generate(self, min_value, max_value, distribution):
        """
        Generate a random number based on provided inputs.

        Args:
            min_value (str): Minimum value as string (use '.' to indicate float)
            max_value (str): Maximum value as string (use '.' to indicate float)
            distribution (str): 'uniform' or 'normal'

        Returns:
            tuple: (value,) where value is int or float (type any_typ)
        """
        # Convert inputs to strings and detect decimal points
        smin = str(min_value)
        smax = str(max_value)
        float_mode = ('.' in smin) or ('.' in smax)

        # Try parsing values
        try:
            if float_mode:
                a = float(smin)
                b = float(smax)
            else:
                a = int(smin)
                b = int(smax)
        except Exception as e:
            # Fallback: attempt float parse then coerce if needed
            try:
                a = float(smin)
                b = float(smax)
                float_mode = True
            except Exception:
                print(f"mbRandom: invalid min/max inputs ('{smin}', '{smax}'), using defaults 0 and 1. Error: {e}")
                a = 0
                b = 1
                float_mode = True

        # Ensure proper ordering
        if a > b:
            a, b = b, a

        # Edge case: identical bounds
        if a == b:
            # Return that exact value, coerced appropriately
            v = float(a) if float_mode else int(a)
            return (v,)

        # Sampling
        if float_mode:
            if distribution == "uniform":
                v = random.uniform(a, b)
            elif distribution == "normal":
                mean = (a + b) / 2.0
                std = (b - a) / 6.0 if (b - a) > 0 else 1.0
                v = random.gauss(mean, std)
                # Clip to range
                v = max(min(v, b), a)
            else:
                v = random.uniform(a, b)
        else:
            # Integer mode
            ia = int(a)
            ib = int(b)
            if distribution == "uniform":
                v = random.randint(ia, ib)
            elif distribution == "normal":
                mean = (ia + ib) / 2.0
                std = max((ib - ia) / 6.0, 1.0)
                v = int(round(random.gauss(mean, std)))
                v = max(min(v, ib), ia)
            else:
                v = random.randint(ia, ib)

        return (v,)
