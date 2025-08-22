import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

// Register the node extension
app.registerExtension({
    name: "Mockba.Plotter",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "mbPlotter") {
            console.log("Registering mbPlotter extension");
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                console.log("mbPlotter node created");
                
                const result = onNodeCreated?.apply(this, arguments);
                
                // Handle execution results
                const originalOnExecuted = this.onExecuted;
                this.onExecuted = (message) => {
                    console.log("Node executed with message:", message);
                    
                    if (originalOnExecuted) {
                        originalOnExecuted.call(this, message);
                    }
                    
                    if (message?.plot_data?.[0]) {
                        const plotData = message.plot_data[0];
                        console.log("Found plot data:", plotData);
                        
                        // Display the plot image directly
                        if (plotData.image_b64) {
                            this.displayPlotImage(plotData.image_b64);
                        }
                    } else {
                        console.log("No plot_data found in message");
                    }
                };
                
                // Add method to display plot image
                this.displayPlotImage = function(imageB64) {
                    console.log("Displaying plot image");
                    
                    // Create or update an image widget instead of DOM manipulation
                    let imageWidget = this.widgets.find(w => w.name === "plot_image");
                    
                    if (!imageWidget) {
                        // Create a new image widget
                        imageWidget = {
                            type: "image",
                            name: "plot_image",
                            value: "",
                            options: {},
                            callback: () => {},
                            computeSize: function() {
                                // Use actual image dimensions if available, otherwise default
                                if (this.image) {
                                    return [this.image.width, this.image.height];
                                }
                                return [512, 256]; // Default fallback
                            },
                            draw: function(ctx, node, widgetWidth, y, widgetHeight) {
                                if (this.image) {
                                    // Draw the image directly on the node canvas
                                    const aspectRatio = this.image.width / this.image.height;
                                    // Use actual image width scaled to fit widget, with padding
                                    const maxWidth = widgetWidth - 20;
                                    const scaledWidth = Math.min(maxWidth, this.image.width);
                                    const drawWidth = scaledWidth;
                                    const drawHeight = drawWidth / aspectRatio;
                                    
                                    ctx.save();
                                    ctx.drawImage(this.image, 10, y + 5, drawWidth, drawHeight);
                                    ctx.restore();
                                    
                                    return [drawWidth + 20, drawHeight + 10];
                                }
                                return [widgetWidth, 20];
                            }
                        };
                        
                        this.widgets.push(imageWidget);
                        console.log("Created image widget");
                    }
                    
                    // Load the image
                    const img = new Image();
                    img.onload = () => {
                        console.log("Image loaded successfully, dimensions:", img.width, "x", img.height);
                        imageWidget.image = img;
                        
                        // Update the widget size now that we have image dimensions
                        imageWidget.size = imageWidget.computeSize();
                        
                        // Force a redraw
                        if (this.graph && this.graph.canvas) {
                            this.graph.canvas.setDirty(true, true);
                        }
                    };
                    
                    img.onerror = (error) => {
                        console.error("Failed to load plot image:", error);
                    };
                    
                    img.src = `data:image/png;base64,${imageB64}`;
                };
                
                return result;
            };
        }
    }
});
