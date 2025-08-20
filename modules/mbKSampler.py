"""
Enhanced K-Sampler Node for ComfyUI
Advanced diffusion model sampling with comprehensive control over noise generation,
sampling parameters, and progressive denoising with preview callbacks.
"""

# Standard library imports
import time

# Third-party imports
import numpy as np
import torch

# ComfyUI imports
import comfy.samplers
import comfy.sample
import comfy.utils
import latent_preview

# Local imports
from .common import CATEGORIES


class mbKSampler:
    """Enhanced K-Sampler with advanced noise control, sampling parameters, and monitoring capabilities."""
    
    # Class constants
    DEFAULT_SEED = 0
    DEFAULT_STEPS = 20
    DEFAULT_CFG = 8.0
    DEFAULT_DENOISE = 1.0
    
    # Sampling limits
    MIN_STEPS = 1
    MAX_STEPS = 10000
    MIN_CFG = 0.0
    MAX_CFG = 100.0
    MIN_DENOISE = 0.0
    MAX_DENOISE = 1.0
    
    # Seed limits (64-bit)
    MIN_SEED = 0
    MAX_SEED = 0xFFFFFFFFFFFFFFFF
    
    def __init__(self):
        """Initialize the enhanced K-Sampler node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for enhanced K-Sampling."""
        return {
            "required": {
                "model": ("MODEL", {
                    "tooltip": "Diffusion model for sampling"
                }),
                "seed": ("INT", {
                    "default": cls.DEFAULT_SEED,
                    "min": cls.MIN_SEED,
                    "max": cls.MAX_SEED,
                    "tooltip": "Random seed for noise generation (0 to 2^64-1)"
                }),
                "steps": ("INT", {
                    "default": cls.DEFAULT_STEPS,
                    "min": cls.MIN_STEPS,
                    "max": cls.MAX_STEPS,
                    "tooltip": "Number of denoising steps"
                }),
                "cfg": ("FLOAT", {
                    "default": cls.DEFAULT_CFG,
                    "min": cls.MIN_CFG,
                    "max": cls.MAX_CFG,
                    "step": 0.1,
                    "tooltip": "Classifier-free guidance scale (higher = more prompt adherence)"
                }),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS, {
                    "tooltip": "Sampling algorithm to use"
                }),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS, {
                    "tooltip": "Noise schedule for denoising process"
                }),
                "positive": ("CONDITIONING", {
                    "tooltip": "Positive conditioning (what you want)"
                }),
                "negative": ("CONDITIONING", {
                    "tooltip": "Negative conditioning (what you don't want)"
                }),
                "latent_image": ("LATENT", {
                    "tooltip": "Input latent image to denoise"
                }),
                "denoise": ("FLOAT", {
                    "default": cls.DEFAULT_DENOISE,
                    "min": cls.MIN_DENOISE,
                    "max": cls.MAX_DENOISE,
                    "step": 0.01,
                    "tooltip": "Denoising strength (1.0 = full denoise, 0.0 = no denoise)"
                }),
            },
            "optional": {
                "disable_noise": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Use zeros instead of random noise (for deterministic results)"
                }),
                "force_full_denoise": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Force full denoising regardless of denoise parameter"
                }),
            },
            "hidden": {
                "start_step": ("INT", {"default": 0, "min": 0, "max": cls.MAX_STEPS}),
                "last_step": ("INT", {"default": cls.MAX_STEPS, "min": 1, "max": cls.MAX_STEPS}),
                "preview_method": (["auto", "none", "latent", "taesd"], {"default": "auto"}),
            }
        }

    # Node metadata
    TITLE = "Enhanced K-Sampler"
    RETURN_TYPES = ("LATENT", "FLOAT", "INT")
    RETURN_NAMES = ("latent", "elapsed_time", "actual_steps")
    FUNCTION = "enhanced_sample"
    CATEGORY = "unset"
    DESCRIPTION = "Enhanced K-Sampler with advanced noise control, partial sampling, preview options, and performance monitoring."

    def enhanced_sample(self, model, seed, steps, cfg, sampler_name, scheduler, positive, negative, 
                       latent_image, denoise=1.0, disable_noise=False, start_step=None, last_step=None, 
                       force_full_denoise=False, preview_method="auto"):
        """
        Perform enhanced K-sampling with comprehensive parameter control.
        
        Args:
            model: Diffusion model for sampling
            seed: Random seed for noise generation
            steps: Number of denoising steps
            cfg: Classifier-free guidance scale
            sampler_name: Sampling algorithm
            scheduler: Noise scheduler
            positive: Positive conditioning
            negative: Negative conditioning
            latent_image: Input latent image
            denoise: Denoising strength (0.0 to 1.0)
            disable_noise: Whether to disable random noise
            start_step: Starting step for partial sampling
            last_step: Last step for partial sampling
            force_full_denoise: Force full denoising
            preview_method: Preview generation method
            
        Returns:
            tuple: (output_latent, elapsed_time, actual_steps_taken)
        """
        try:
            start_time = time.time()
            
            # Validate and prepare parameters
            validated_params = self._validate_sampling_parameters(
                steps, cfg, denoise, start_step, last_step
            )
            
            # Generate noise
            noise = self._prepare_sampling_noise(
                latent_image, seed, disable_noise
            )
            
            # Setup preview callback
            callback = self._setup_preview_callback(model, steps, preview_method)
            
            # Perform sampling
            samples = self._execute_sampling(
                model=model,
                noise=noise,
                steps=validated_params["steps"],
                cfg=validated_params["cfg"],
                sampler_name=sampler_name,
                scheduler=scheduler,
                positive=positive,
                negative=negative,
                latent_image=latent_image,
                denoise=validated_params["denoise"],
                disable_noise=disable_noise,
                start_step=validated_params["start_step"],
                last_step=validated_params["last_step"],
                force_full_denoise=force_full_denoise,
                callback=callback,
                seed=seed
            )
            
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            
            # Calculate actual steps taken
            actual_steps = self._calculate_actual_steps(
                validated_params["steps"], 
                validated_params["start_step"], 
                validated_params["last_step"],
                validated_params["denoise"]
            )
            
            # Prepare output
            output_latent = latent_image.copy()
            output_latent["samples"] = samples
            
            print(f"Sampling completed: {actual_steps} steps, {elapsed_time:.2f}s, "
                  f"{sampler_name} + {scheduler}, CFG: {cfg}")
            
            return (output_latent, elapsed_time, actual_steps)
            
        except Exception as e:
            error_msg = f"Sampling failed: {str(e)}"
            print(error_msg)
            # Return original latent on error
            return (latent_image, 0.0, 0)

    def _validate_sampling_parameters(self, steps, cfg, denoise, start_step, last_step):
        """Validate and normalize sampling parameters."""
        # Clamp values to valid ranges
        validated_steps = max(self.MIN_STEPS, min(self.MAX_STEPS, steps))
        validated_cfg = max(self.MIN_CFG, min(self.MAX_CFG, cfg))
        validated_denoise = max(self.MIN_DENOISE, min(self.MAX_DENOISE, denoise))
        
        # Handle optional step parameters
        validated_start_step = start_step if start_step is not None else 0
        validated_last_step = last_step if last_step is not None else validated_steps
        
        # Ensure step order is logical
        validated_start_step = max(0, min(validated_steps, validated_start_step))
        validated_last_step = max(validated_start_step, min(validated_steps, validated_last_step))
        
        return {
            "steps": validated_steps,
            "cfg": validated_cfg,
            "denoise": validated_denoise,
            "start_step": validated_start_step,
            "last_step": validated_last_step
        }

    def _prepare_sampling_noise(self, latent_image, seed, disable_noise):
        """Prepare noise for sampling with enhanced control."""
        latent_samples = latent_image["samples"]
        
        if disable_noise:
            # Create zero noise for deterministic results
            noise = torch.zeros(
                latent_samples.size(),
                dtype=latent_samples.dtype,
                layout=latent_samples.layout,
                device=latent_samples.device,
            )
        else:
            # Use standard ComfyUI noise preparation with proper batch handling
            batch_indices = latent_image.get("batch_index", None)
            noise = comfy.sample.prepare_noise(latent_samples, seed, batch_indices)
        
        return noise

    def _setup_preview_callback(self, model, steps, preview_method):
        """Setup preview callback based on method selection."""
        if preview_method == "none":
            return None
        elif preview_method == "auto":
            return latent_preview.prepare_callback(model, steps)
        else:
            # For specific methods, try to use them if available
            try:
                return latent_preview.prepare_callback(model, steps, preview_method)
            except Exception:
                # Fallback to auto if specific method fails
                return latent_preview.prepare_callback(model, steps)

    def _execute_sampling(self, model, noise, steps, cfg, sampler_name, scheduler, 
                         positive, negative, latent_image, denoise, disable_noise,
                         start_step, last_step, force_full_denoise, callback, seed):
        """Execute the actual sampling process."""
        # Extract latent samples
        latent_samples = latent_image["samples"]
        
        # Fix empty latent channels to match model requirements
        latent_samples = comfy.sample.fix_empty_latent_channels(model, latent_samples)
        
        # Extract noise mask if present
        noise_mask = latent_image.get("noise_mask", None)
        
        # Check progress bar setting
        disable_pbar = not comfy.utils.PROGRESS_BAR_ENABLED
        
        # Perform sampling
        samples = comfy.sample.sample(
            model=model,
            noise=noise,
            steps=steps,
            cfg=cfg,
            sampler_name=sampler_name,
            scheduler=scheduler,
            positive=positive,
            negative=negative,
            latent_image=latent_samples,
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
        
        return samples

    def _calculate_actual_steps(self, total_steps, start_step, last_step, denoise):
        """Calculate the actual number of steps that will be performed."""
        if start_step is None:
            start_step = 0
        if last_step is None:
            last_step = total_steps
        
        # Calculate effective steps based on denoise amount
        effective_steps = int(total_steps * denoise)
        actual_start = min(start_step, effective_steps)
        actual_end = min(last_step, effective_steps)
        
        return max(0, actual_end - actual_start)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        """Validate input parameters for the sampler."""
        # Validate seed range
        if "seed" in kwargs:
            seed = kwargs["seed"]
            if not (cls.MIN_SEED <= seed <= cls.MAX_SEED):
                return f"Seed must be between {cls.MIN_SEED} and {cls.MAX_SEED}"
        
        # Validate steps
        if "steps" in kwargs:
            steps = kwargs["steps"]
            if not (cls.MIN_STEPS <= steps <= cls.MAX_STEPS):
                return f"Steps must be between {cls.MIN_STEPS} and {cls.MAX_STEPS}"
        
        # Validate CFG
        if "cfg" in kwargs:
            cfg = kwargs["cfg"]
            if not (cls.MIN_CFG <= cfg <= cls.MAX_CFG):
                return f"CFG must be between {cls.MIN_CFG} and {cls.MAX_CFG}"
        
        # Validate denoise
        if "denoise" in kwargs:
            denoise = kwargs["denoise"]
            if not (cls.MIN_DENOISE <= denoise <= cls.MAX_DENOISE):
                return f"Denoise must be between {cls.MIN_DENOISE} and {cls.MAX_DENOISE}"
        
        # Validate step range consistency
        if "start_step" in kwargs and "last_step" in kwargs:
            start_step = kwargs.get("start_step", 0)
            last_step = kwargs.get("last_step", 10000)
            if start_step is not None and last_step is not None and start_step > last_step:
                return "Start step cannot be greater than last step"
        
        return True
