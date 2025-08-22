import { app } from "../../scripts/app.js";

class mbPlotter {
    constructor(node) {
        this.node = node;

        // Handle execution output to draw the plot
        this.node.onExecuted = function(message) {
            if (message && message.plot_data && message.plot_data.length > 0) {
                const plotData = message.plot_data[0];
                console.log("Found plot data:", plotData);
                
                // Update node title to match the actual plot title
                if (plotData.plot_name) {
                    this.title = plotData.plot_name;
                }
                
                if (plotData.image_b64) {
                    // Find or create image widget
                    let imageWidget = null;
                    if (this.widgets) {
                        imageWidget = this.widgets.find(w => w && w.name === "plot_image");
                    }
                    
                    if (!imageWidget) {
                        imageWidget = {
                            type: "image",
                            name: "plot_image",
                            value: "",
                            draw: function(ctx, node, widgetWidth, y) {
                                if (this.image) {
                                    const aspectRatio = this.image.width / this.image.height;
                                    const maxWidth = widgetWidth - 20;
                                    const drawWidth = Math.min(maxWidth, 400);
                                    const drawHeight = drawWidth / aspectRatio;
                                    
                                    ctx.drawImage(this.image, 10, y + 5, drawWidth, drawHeight);
                                    return [drawWidth + 20, drawHeight + 10];
                                }
                                return [widgetWidth, 30];
                            }
                        };
                        
                        this.widgets = this.widgets || [];
                        this.widgets.push(imageWidget);
                        console.log("Created image widget");
                    }
                    
                    // Load and display the image
                    const img = new Image();
                    img.onload = () => {
                        console.log("Image loaded successfully");
                        imageWidget.image = img;
                        
                        // Force redraw
                        if (this.graph && this.graph.canvas) {
                            this.graph.canvas.setDirty(true);
                        }
                    };
                    
                    img.onerror = (error) => {
                        console.error("Failed to load plot image:", error);
                    };
                    
                    img.src = `data:image/png;base64,${plotData.image_b64}`;
                }
            }
        };
    }
}

// Register the extension
app.registerExtension({
    name: "Mockba.Plotter",
    async beforeRegisterNodeDef(nodeType, nodeData, _app) {
        if (nodeData.name === "mbPlotter") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                if (onNodeCreated) onNodeCreated.apply(this, []);
                this.mbPlotter = new mbPlotter(this);
            };
        }
    }
});
