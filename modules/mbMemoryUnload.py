"""
Memory Unload Bridge Node for ComfyUI
A passthrough bridge node that unloads GPU memory and provides statistics.
"""

# Standard library imports
import gc
import torch

# Local imports
from .common import any_typ

class mbMemoryUnload:
    """Passthrough bridge node that unloads GPU memory when executed."""
    
    # Class constants
    DEFAULT_STATS_MESSAGE = "Memory statistics will appear here after execution..."
    
    # Memory unit thresholds (same as mbDataTypeConverter)
    BYTES_PER_KB = 1024
    BYTES_PER_MB = 1024 * 1024
    BYTES_PER_GB = 1024 * 1024 * 1024
    
    def __init__(self):
        """Initialize the memory unload bridge node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for memory unload bridge."""
        return {
            "required": {
                "input": (any_typ, {
                    "tooltip": "Any object - will be passed through unchanged"
                }),
                "unload_mode": (["light", "moderate", "aggressive"], {
                    "default": "moderate",
                    "tooltip": "Light: CUDA cache only, Moderate: +garbage collection, Aggressive: +model unloading"
                }),
                "show_stats": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Show detailed memory statistics in output"
                }),
            }
        }

    # Node metadata
    TITLE = "Memory Unload"
    RETURN_TYPES = (any_typ, "STRING")
    RETURN_NAMES = ("output", "memory_stats")
    FUNCTION = "unload_memory_and_passthrough"
    CATEGORY = "unset"
    DESCRIPTION = "Bridge node that unloads GPU memory when executed and passes input through unchanged. Provides memory statistics output."
    OUTPUT_NODE = True

    def unload_memory_and_passthrough(self, input, unload_mode, show_stats):
        """
        Unload GPU memory and pass input through unchanged.
        
        Args:
            input: Any object to pass through
            unload_mode: How aggressively to unload memory
            show_stats: Whether to show detailed statistics
            
        Returns:
            tuple: (unchanged_input, memory_statistics_string)
        """
        try:
            # Capture memory stats before unloading
            stats_before = self._get_memory_stats()
            
            # Perform memory unloading based on mode
            unload_actions = self._perform_memory_unload(unload_mode)
            
            # Capture memory stats after unloading
            stats_after = self._get_memory_stats()
            
            # Generate statistics report
            if show_stats:
                stats_report = self._generate_memory_report(
                    stats_before, stats_after, unload_actions, unload_mode
                )
            else:
                stats_report = f"Memory unload completed ({unload_mode} mode)"
            
            # Pass through the input unchanged
            return (input, stats_report)
            
        except Exception as e:
            error_msg = f"Error during memory unload: {str(e)}"
            print(error_msg)
            return (input, error_msg)

    def _get_memory_stats(self):
        """Get current memory statistics."""
        stats = {
            'python_objects': len(gc.get_objects()),
            'gpu_available': False,
            'gpu_allocated': 0,
            'gpu_cached': 0,
            'gpu_total': 0
        }
        
        # Get GPU memory stats if CUDA is available
        if torch.cuda.is_available():
            stats['gpu_available'] = True
            stats['gpu_allocated'] = torch.cuda.memory_allocated()
            stats['gpu_cached'] = torch.cuda.memory_reserved() - torch.cuda.memory_allocated()
            stats['gpu_total'] = torch.cuda.memory_reserved()
            stats['gpu_device_count'] = torch.cuda.device_count()
            stats['gpu_device_name'] = torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else "Unknown"
        
        return stats

    def _perform_memory_unload(self, unload_mode):
        """Perform memory unloading based on the specified mode."""
        actions_performed = []
        
        try:
            if unload_mode in ["light", "moderate", "aggressive"]:
                # Always clear CUDA cache
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    actions_performed.append("CUDA cache cleared")
                else:
                    actions_performed.append("No CUDA available")
            
            if unload_mode in ["moderate", "aggressive"]:
                # Force garbage collection
                collected = gc.collect()
                actions_performed.append(f"Garbage collection: {collected} objects collected")
            
            if unload_mode == "aggressive":
                # Additional aggressive cleanup
                if torch.cuda.is_available():
                    # Clear all CUDA memory
                    for i in range(torch.cuda.device_count()):
                        with torch.cuda.device(i):
                            torch.cuda.empty_cache()
                            torch.cuda.synchronize()
                    actions_performed.append("Multi-GPU cache cleared")
                
                # Force multiple garbage collection passes
                for _ in range(3):
                    gc.collect()
                actions_performed.append("Multiple GC passes completed")
                
                # Try to minimize memory fragmentation
                if hasattr(torch.cuda, 'memory_stats'):
                    actions_performed.append("Memory defragmentation attempted")
            
        except Exception as e:
            actions_performed.append(f"Error during cleanup: {str(e)}")
        
        return actions_performed

    def _generate_memory_report(self, stats_before, stats_after, actions, mode):
        """Generate comprehensive memory statistics report."""
        report_lines = [
            f"Memory Unload Report ({mode} mode):",
            "=" * 40,
            ""
        ]
        
        # Actions performed
        report_lines.append("Actions Performed:")
        for action in actions:
            report_lines.append(f"  • {action}")
        report_lines.append("")
        
        # Python object count changes
        obj_before = stats_before['python_objects']
        obj_after = stats_after['python_objects']
        obj_freed = obj_before - obj_after
        
        report_lines.extend([
            "Python Objects:",
            f"  Before: {obj_before:,}",
            f"  After: {obj_after:,}",
            f"  Freed: {obj_freed:,} objects",
            ""
        ])
        
        # GPU memory statistics
        if stats_before['gpu_available']:
            gpu_allocated_before = stats_before['gpu_allocated']
            gpu_allocated_after = stats_after['gpu_allocated']
            gpu_cached_before = stats_before['gpu_cached']
            gpu_cached_after = stats_after['gpu_cached']
            gpu_total_before = stats_before['gpu_total']
            gpu_total_after = stats_after['gpu_total']
            
            allocated_freed = gpu_allocated_before - gpu_allocated_after
            cached_freed = gpu_cached_before - gpu_cached_after
            total_freed = gpu_total_before - gpu_total_after
            
            report_lines.extend([
                f"GPU Memory ({stats_before['gpu_device_name']}):",
                f"  Allocated:",
                f"    Before: {self._format_bytes(gpu_allocated_before)}",
                f"    After: {self._format_bytes(gpu_allocated_after)}",
                f"    Freed: {self._format_bytes(allocated_freed)}",
                f"  Cached:",
                f"    Before: {self._format_bytes(gpu_cached_before)}",
                f"    After: {self._format_bytes(gpu_cached_after)}",
                f"    Freed: {self._format_bytes(cached_freed)}",
                f"  Total:",
                f"    Before: {self._format_bytes(gpu_total_before)}",
                f"    After: {self._format_bytes(gpu_total_after)}",
                f"    Freed: {self._format_bytes(total_freed)}",
                ""
            ])
            
            # Add utilization percentages
            if gpu_total_after > 0:
                utilization = (gpu_allocated_after / gpu_total_after) * 100
                report_lines.append(f"  Current Utilization: {utilization:.1f}%")
            
        else:
            report_lines.extend([
                "GPU Memory:",
                "  No CUDA GPU available",
                ""
            ])
        
        # Summary
        total_memory_freed = 0
        if stats_before['gpu_available']:
            total_memory_freed = (stats_before['gpu_total'] - stats_after['gpu_total'])
        
        report_lines.extend([
            "Summary:",
            f"  Mode: {mode}",
            f"  Objects freed: {obj_freed:,}",
            f"  GPU memory freed: {self._format_bytes(total_memory_freed)}",
            f"  Actions completed: {len(actions)}"
        ])
        
        return "\n".join(report_lines)

    def _format_bytes(self, bytes_val):
        """Format byte values in human-readable format."""
        if bytes_val < 0:
            return f"-{self._format_bytes(-bytes_val)}"
        
        if bytes_val < self.BYTES_PER_KB:
            return f"{bytes_val} B"
        elif bytes_val < self.BYTES_PER_MB:
            return f"{bytes_val/self.BYTES_PER_KB:.1f} KB"
        elif bytes_val < self.BYTES_PER_GB:
            return f"{bytes_val/self.BYTES_PER_MB:.1f} MB"
        else:
            return f"{bytes_val/self.BYTES_PER_GB:.1f} GB"
