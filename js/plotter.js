import { app } from "../../scripts/app.js";

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
                
                // Initialize properties for right-click configuration
                this.properties = this.properties || {};
                this.properties.plot_name = this.properties.plot_name || "Plot";
                this.properties.history_size = this.properties.history_size || 512;
                this.properties.width = this.properties.width || 512;
                this.properties.height = this.properties.height || 256;
                this.properties.line_color = this.properties.line_color || "#00FF00";
                this.properties.background_color = this.properties.background_color || "#222222";
                this.properties.auto_scale = this.properties.auto_scale !== undefined ? this.properties.auto_scale : true;
                this.properties.y_min = this.properties.y_min !== undefined ? this.properties.y_min : -1.0;
                this.properties.y_max = this.properties.y_max !== undefined ? this.properties.y_max : 1.0;
                this.properties.show_grid = this.properties.show_grid !== undefined ? this.properties.show_grid : true;
                this.properties.reset_plot = this.properties.reset_plot !== undefined ? this.properties.reset_plot : false;
                
                // Set initial title
                this.title = this.properties.plot_name || "Plot";
                
                // Simple property change handler
                this.onPropertyChanged = function(propName) {
                    console.log("Property changed:", propName, this.properties[propName]);
                    
                    // Update node title when plot_name changes
                    if (propName === 'plot_name') {
                        this.title = this.properties.plot_name || "Plot";
                    }
                    
                    // Update corresponding widget if it exists
                    if (this.widgets) {
                        for (let i = 0; i < this.widgets.length; i++) {
                            if (this.widgets[i] && this.widgets[i].name === propName) {
                                this.widgets[i].value = this.properties[propName];
                                break;
                            }
                        }
                    }
                };
                
                // Hide the configuration widgets after a delay
                setTimeout(() => {
                    if (this.widgets) {
                        const hiddenWidgets = ["plot_name", "history_size", "width", "height", "line_color", 
                                             "background_color", "auto_scale", "y_min", "y_max", "show_grid", "reset_plot"];
                        for (let i = 0; i < this.widgets.length; i++) {
                            const widget = this.widgets[i];
                            if (widget && hiddenWidgets.includes(widget.name)) {
                                widget.hidden = true;
                                widget.type = "hidden";
                            }
                        }
                    }
                }, 200);
                
                // Handle execution results
                const originalOnExecuted = this.onExecuted;
                this.onExecuted = (message) => {
                    console.log("Node executed with message:", message);
                    
                    if (originalOnExecuted) {
                        originalOnExecuted.call(this, message);
                    }
                    
                    if (message && message.plot_data && message.plot_data.length > 0) {
                        const plotData = message.plot_data[0];
                        console.log("Found plot data:", plotData);
                        
                        if (plotData.image_b64) {
                            this.displayPlotImage(plotData.image_b64);
                        }
                    }
                };
                
                // Simple image display method
                this.displayPlotImage = function(imageB64) {
                    console.log("Displaying plot image");
                    
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
                    
                    img.src = `data:image/png;base64,${imageB64}`;
                };
                
                return result;
            };
        }
    }
});
