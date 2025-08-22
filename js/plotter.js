import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

class mbPlotterController {
    constructor(node) {
        this.node = node;
        
        // Initialize properties for right-click configuration
        this.node.properties = this.node.properties || {};
        this.node.properties.history_size = 512;
        this.node.properties.width = 512;
        this.node.properties.height = 256;
        this.node.properties.line_color = "#00FF00";
        this.node.properties.background_color = "#222222";
        this.node.properties.auto_scale = true;
        this.node.properties.y_min = -1.0;
        this.node.properties.y_max = 1.0;
        this.node.properties.show_grid = true;
        
        this.setupPropertyHandlers();
    }
    
    setupPropertyHandlers() {
        // Handle property changes to update hidden widgets
        this.node.onPropertyChanged = function(propName) {
            console.log("Property changed:", propName, this.properties[propName]);
            
            // Update the corresponding hidden widgets with new property values
            const propertyToWidget = {
                'history_size': 1,
                'width': 2, 
                'height': 3,
                'line_color': 4,
                'background_color': 5,
                'auto_scale': 6,
                'y_min': 7,
                'y_max': 8,
                'show_grid': 9
            };
            
            if (propertyToWidget[propName] !== undefined) {
                const widgetIndex = propertyToWidget[propName];
                if (this.widgets[widgetIndex]) {
                    this.widgets[widgetIndex].value = this.properties[propName];
                }
            }
            
            // Force graph to recognize changes
            if (this.graph) {
                this.graph.setisChangedFlag(this.id);
            }
        };
        
        // Initialize widget values from properties
        this.node.onGraphConfigured = function() {
            this.configured = true;
            // Update all hidden widgets with property values
            const properties = ['history_size', 'width', 'height', 'line_color', 'background_color', 'auto_scale', 'y_min', 'y_max', 'show_grid'];
            properties.forEach((prop, index) => {
                if (this.widgets[index + 1]) {
                    this.widgets[index + 1].value = this.properties[prop];
                }
            });
        };
    }
}

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
                
                // Create the plotter controller for property management
                this.plotterController = new mbPlotterController(this);
                
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
                        
                        // Force immediate redraw with multiple methods
                        if (this.graph && this.graph.canvas) {
                            this.graph.canvas.setDirty(true, true);
                            this.graph.canvas.draw(true, true);
                        }
                        
                        // Also force node redraw
                        if (this.setDirtyCanvas) {
                            this.setDirtyCanvas(true, true);
                        }
                        
                        // Schedule a redraw on the next frame
                        requestAnimationFrame(() => {
                            if (this.graph && this.graph.canvas) {
                                this.graph.canvas.setDirty(true, true);
                                this.graph.canvas.draw(true, true);
                            }
                        });
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
