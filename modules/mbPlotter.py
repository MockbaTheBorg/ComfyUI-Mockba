"""
Plotter Node for ComfyUI
Creates time-series plots using matplotlib with JavaScript display.
"""

# Standard library imports
import json
import base64
from io import BytesIO
from collections import deque

# Third-party imports
import numpy as np
import torch
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("matplotlib not available - mbPlotter will not work")

# Local imports
from .common import CATEGORIES, convert_pil_to_tensor


class mbPlotter:
    """Plot values over time using matplotlib with JavaScript display."""
    
    # Class constants
    DEFAULT_WIDTH = 512
    DEFAULT_HEIGHT = 256
    DEFAULT_HISTORY_SIZE = DEFAULT_WIDTH
    
    # Global storage for plot data (keyed by unique_id)
    _plot_data = {}
    
    def __init__(self):
        """Initialize the plotter node."""
        # Generate a unique identifier for this node instance
        import uuid
        self._unique_id = str(uuid.uuid4())[:8]  # Short unique ID
        
    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for the plotter."""
        return {
            "required": {
                "value": ("FLOAT", {
                    "forceInput": True,
                    "tooltip": "Value to plot on the chart"
                }),
             },
            "hidden": {
                "plot_name": ("STRING", {
                    "default": "Plot",
                    "tooltip": "Name of the plot"
                }),
               "history_size": ("INT", {
                    "default": cls.DEFAULT_HISTORY_SIZE,
                    "min": 50,
                    "max": 2048,
                    "tooltip": "Number of data points to keep in history"
                }),
                "width": ("INT", {
                    "default": cls.DEFAULT_WIDTH,
                    "min": 200,
                    "max": 1024,
                    "tooltip": "Width of the plot image"
                }),
                "height": ("INT", {
                    "default": cls.DEFAULT_HEIGHT,
                    "min": 150,
                    "max": 512,
                    "tooltip": "Height of the plot image"
                }),
                "line_color": ("STRING", {
                    "default": "#00FF00",
                    "tooltip": "Line color (hex format with #)"
                }),
                "background_color": ("STRING", {
                    "default": "#222222",
                    "tooltip": "Background color (hex format with #)"
                }),
                "auto_scale": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Automatically scale Y-axis to fit data"
                }),
                "y_min": ("FLOAT", {
                    "default": -1.0,
                    "tooltip": "Y-axis minimum (used when auto_scale is False)"
                }),
                "y_max": ("FLOAT", {
                    "default": 1.0,
                    "tooltip": "Y-axis maximum (used when auto_scale is False)"
                }),
                "show_grid": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Show grid lines"
                }),
                "reset_plot": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Reset the plot data"
                }),
            },
        }

    # Node metadata
    TITLE = "Value Plotter"
    RETURN_TYPES = ("IMAGE", "FLOAT", "STRING")
    RETURN_NAMES = ("image", "current_value", "plot_data")
    FUNCTION = "plot_value"
    CATEGORY = CATEGORIES["DEVELOPMENT"]
    DESCRIPTION = "Plot values over time using matplotlib with real-time JavaScript display."
    OUTPUT_NODE = True
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """Force execution every time by returning a unique value."""
        import time
        return time.time()

    def plot_value(self, value, plot_name=None, history_size=None, width=None, height=None,
                   line_color=None, background_color=None, auto_scale=None, 
                   y_min=None, y_max=None, show_grid=None, reset_plot=None):
        """
        Plot a value on the time-series chart using matplotlib.
        
        Returns:
            A dictionary containing the UI data and the result tuple.
        """
        if not MATPLOTLIB_AVAILABLE:
            # Return error image
            error_img = np.zeros((height or self.DEFAULT_HEIGHT, width or self.DEFAULT_WIDTH, 3), dtype=np.uint8)
            error_img[:, :, 0] = 255  # Red background
            image_tensor = torch.from_numpy(error_img.astype(np.float32) / 255.0)[None,]
            return {"ui": {"plot_image": "matplotlib not available"}, "result": (image_tensor, value, "error")}
        
        try:
            # Use unique node ID as key instead of plot_name
            node_key = self._unique_id
            
            # Use defaults for hidden parameters
            plot_name = plot_name or "Plot"  # Default plot name if not provided
            history_size = history_size or self.DEFAULT_HISTORY_SIZE
            width = width or self.DEFAULT_WIDTH
            height = height or self.DEFAULT_HEIGHT
            line_color = line_color or "#00FF00"
            background_color = background_color or "#222222"
            auto_scale = auto_scale if auto_scale is not None else True
            y_min = y_min if y_min is not None else -1.0
            y_max = y_max if y_max is not None else 1.0
            show_grid = show_grid if show_grid is not None else True
            reset_plot = reset_plot if reset_plot is not None else False
            
            # Initialize or reset plot data using unique node key
            if reset_plot or node_key not in self._plot_data:
                self._plot_data[node_key] = {
                    'values': deque(maxlen=history_size),
                    'min_val': float('inf'),
                    'max_val': float('-inf')
                }
            
            # Update history size if changed
            if len(self._plot_data[node_key]['values']) > 0:
                current_maxlen = self._plot_data[node_key]['values'].maxlen
                if current_maxlen != history_size:
                    # Convert to list, update maxlen, convert back
                    old_values = list(self._plot_data[node_key]['values'])
                    self._plot_data[node_key]['values'] = deque(old_values, maxlen=history_size)
            
            # Add new value
            plot_data = self._plot_data[node_key]
            plot_data['values'].append(value)
            
            # Update min/max for auto-scaling
            if auto_scale:
                plot_data['min_val'] = min(plot_data['min_val'], value)
                plot_data['max_val'] = max(plot_data['max_val'], value)
                current_y_min = plot_data['min_val']
                current_y_max = plot_data['max_val']
                # Add some padding
                y_range = current_y_max - current_y_min
                if y_range > 0:
                    padding = y_range * 0.1
                    current_y_min -= padding
                    current_y_max += padding
                else:
                    # If all values are the same, add some range
                    current_y_min = value - 0.5
                    current_y_max = value + 0.5
            else:
                current_y_min = y_min
                current_y_max = y_max
            
            # Generate plot using matplotlib
            plot_image_b64 = self._generate_matplotlib_plot(
                list(plot_data['values']), 
                width, height, 
                line_color, background_color, 
                current_y_min, current_y_max, 
                show_grid, f"Plot {node_key}" if plot_name == "Plot" else plot_name
            )
            
            # Convert plot to tensor for output
            image_tensor = self._b64_to_tensor(plot_image_b64, width, height)
            
            # Prepare data for JavaScript display
            plot_data_json = {
                'plot_name': f"Plot {node_key}" if plot_name == "Plot" else plot_name,
                'current_value': float(value),
                'data_points': len(plot_data['values']),
                'y_min': float(current_y_min),
                'y_max': float(current_y_max),
                'image_b64': plot_image_b64
            }
            
            return {
                "ui": {"plot_data": [plot_data_json]}, 
                "result": (image_tensor, value, json.dumps(plot_data_json))
            }
            
        except Exception as e:
            print(f"Error in plotter: {e}")
            # Return error image
            error_img = np.zeros((height or self.DEFAULT_HEIGHT, width or self.DEFAULT_WIDTH, 3), dtype=np.uint8)
            error_img[:, :, 0] = 255  # Red background
            image_tensor = torch.from_numpy(error_img.astype(np.float32) / 255.0)[None,]
            return {"ui": {"plot_data": [{"error": str(e)}]}, "result": (image_tensor, value, f"error: {e}")}

    def _generate_matplotlib_plot(self, values, width, height, line_color, bg_color, y_min, y_max, show_grid, title):
        """Generate a plot using matplotlib and return as base64."""
        if not MATPLOTLIB_AVAILABLE:
            return ""
        
        # Import matplotlib locally to avoid linting issues
        import matplotlib.pyplot as plt
        from matplotlib.ticker import MaxNLocator
            
        # Create figure with specified size
        dpi = 100
        fig_width = width / dpi
        fig_height = height / dpi
        
        plt.ioff()  # Turn off interactive mode
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        
        # Plot the data
        if len(values) > 0:
            x_values = range(len(values))
            ax.plot(x_values, values, color=line_color, linewidth=1.5)
        
        # Configure the plot
        ax.set_ylim(y_min, y_max)
        ax.set_xlim(0, len(values) if len(values) > 1 else 1)
        
        # Add title
        ax.set_title(title, color='white', fontsize=10, pad=10)
        
        # Grid and axes styling
        if show_grid:
            ax.grid(True, alpha=0.3, color='white', linestyle='--', linewidth=0.5)
            # Show ticks and labels for better readability
            ax.tick_params(axis='both', which='major', labelsize=8, colors='white', length=3)
            # Set tick positions for better scale visibility
            ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
            ax.xaxis.set_major_locator(MaxNLocator(nbins=6))
            # Keep axis spines subtle but visible
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(0.8)
                spine.set_alpha(0.4)
                spine.set_color('white')
        else:
            # Minimal styling when no grid
            ax.set_xticks([])
            ax.set_yticks([])
            # Remove axes completely when no grid
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
        
        # Add current value annotation if we have data
        if len(values) > 0:
            current_val = values[-1]
            ax.annotate(f'{current_val:.3f}', 
                       xy=(len(values)-1, current_val),
                       xytext=(10, 10), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7),
                       color='white', fontsize=8, ha='left')
        
        # Tight layout
        plt.tight_layout(pad=0)
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', facecolor=bg_color, 
                   bbox_inches='tight', pad_inches=0, dpi=dpi)
        buffer.seek(0)
        
        image_b64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return image_b64

    def _b64_to_tensor(self, image_b64, width, height):
        """Convert base64 image to tensor."""
        try:
            from PIL import Image
            import base64
            
            # Decode base64
            image_data = base64.b64decode(image_b64)
            image = Image.open(BytesIO(image_data)).convert('RGB')
            
            # Resize if needed
            if image.size != (width, height):
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convert to tensor
            return convert_pil_to_tensor(image)
            
        except Exception as e:
            print(f"Error converting b64 to tensor: {e}")
            # Return black image
            black_img = np.zeros((height, width, 3), dtype=np.uint8)
            return torch.from_numpy(black_img.astype(np.float32) / 255.0)[None,]
