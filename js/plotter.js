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
                                        // Determine node dimensions (fallback to widgetWidth)
                                        const nodeWidth = (node && node.size && node.size[0]) ? node.size[0] : widgetWidth;
                                        const nodeHeight = (node && node.size && node.size[1]) ? node.size[1] : (this.image.height + 20);

                                        const padding = 8;

                                        // Available drawing area inside the node for this widget
                                        const availW = Math.max(20, nodeWidth - padding * 2);
                                        // Compute available height below the widget y coordinate
                                        const availH = Math.max(20, nodeHeight - y - padding - 4);

                                        const aspectRatio = this.image.width / this.image.height;

                                        // Fit preserving aspect ratio within availW x availH
                                        let drawWidth = availW;
                                        let drawHeight = drawWidth / aspectRatio;
                                        if (drawHeight > availH) {
                                            drawHeight = availH;
                                            drawWidth = drawHeight * aspectRatio;
                                        }

                                        // Center the image inside the node area
                                        const drawX = Math.round((nodeWidth - drawWidth) / 2);
                                        const drawY = Math.round(y + ((availH - drawHeight) / 2) + 4);

                                        ctx.drawImage(this.image, drawX, drawY, drawWidth, drawHeight);
                                        return [widgetWidth, drawHeight + 10];
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
                        // Try node-level redraw API first, then fallback to graph-level
                        try {
                            if (typeof this.setDirtyCanvas === 'function') {
                                this.setDirtyCanvas(true, true);
                                return;
                            }
                        } catch (e) {
                            // ignore
                        }

                        if (this.graph && this.graph.canvas) {
                            this.graph.canvas.setDirty(true);
                        }

                        if (app && app.graph && typeof app.graph.setDirtyCanvas === 'function') {
                            app.graph.setDirtyCanvas(true, true);
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
