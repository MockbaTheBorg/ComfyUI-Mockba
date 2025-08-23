import { app } from "../../scripts/app.js";

// Define default properties
const SHOW_DIMENSIONS = false;

class mbImageShow {
    constructor(node) {
        this.node = node;
        this.node.properties = this.node.properties || {};

        // Initialize properties with defaults
        this.node.properties.show_dimensions = this.node.properties.show_dimensions ?? SHOW_DIMENSIONS;

        this.node.onConfigure = function() {
            // Called when loading from workflow - ensure properties are valid
            this.properties = this.properties || {};
            this.properties.show_dimensions = this.properties.show_dimensions ?? SHOW_DIMENSIONS;
        };

        this.node.onGraphConfigured = function() {
            this.configured = true;
            this.onPropertyChanged();
        };

        this.node.onPropertyChanged = function(propName) {
            if (!this.configured) return;
            
            // Validate properties
            if (typeof this.properties.show_dimensions !== 'boolean') {
                this.properties.show_dimensions = SHOW_DIMENSIONS;
            }
        };

        this.node.onExecuted = function(message) {
            if (message && message.image_show && message.image_show.length > 0) {
                const item = message.image_show[0];
                if (item.title) {
                    this.title = item.title;
                }

                if (item.image_b64) {
                    let imageWidget = null;
                    if (this.widgets) {
                        imageWidget = this.widgets.find(w => w && w.name === "image_show");
                    }

                    if (!imageWidget) {
                        imageWidget = {
                            type: "image",
                            name: "image_show",
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

                                    // If dimensions text will be shown, reserve vertical space so the text fits
                                    const showDims = node && node.properties && node.properties.show_dimensions;
                                    const dimFontSize = 10; // slightly smaller font
                                    const reservedTextHeight = showDims ? (dimFontSize + 8) : 0;

                                    // Fit preserving aspect ratio within availW x (availH - reservedTextHeight)
                                    const imageAvailH = Math.max(10, availH - reservedTextHeight);
                                    let drawWidth = availW;
                                    let drawHeight = drawWidth / aspectRatio;
                                    if (drawHeight > imageAvailH) {
                                        drawHeight = imageAvailH;
                                        drawWidth = drawHeight * aspectRatio;
                                    }

                                    // Center the image inside the node area
                                    const drawX = Math.round((nodeWidth - drawWidth) / 2);
                                    const drawY = Math.round(y + ((availH - drawHeight) / 2) + 4);

                                    ctx.drawImage(this.image, drawX, drawY, drawWidth, drawHeight);

                                    // Optionally draw image dimensions centered below the image
                                    let extraHeight = 10;
                                    try {
                                        if (showDims) {
                                            const text = `${this.image.width}×${this.image.height}`;
                                            const fontSize = dimFontSize;
                                            // Save/restore canvas state
                                            ctx.save();
                                            ctx.font = `${fontSize}px sans-serif`;
                                            ctx.textAlign = 'center';
                                            ctx.textBaseline = 'top';
                                            // Semi-opaque text color for readability
                                            ctx.fillStyle = 'rgba(170,170,170,0.85)';

                                            const textX = Math.round(drawX + drawWidth / 2);
                                            const textY = Math.round(drawY + drawHeight + 3);

                                            // Draw text
                                            ctx.fillText(text, textX, textY);
                                            ctx.restore();

                                            extraHeight = fontSize + 8; // include small padding
                                        }
                                    } catch (e) {
                                        // If anything goes wrong, fall back to default spacing
                                        extraHeight = 10;
                                    }

                                    // Return widget used width and height (system uses this to layout)
                                    return [widgetWidth, drawHeight + extraHeight];
                                }
                                return [widgetWidth, 30];
                            }
                        };

                        this.widgets = this.widgets || [];
                        this.widgets.push(imageWidget);
                    }

                    const img = new Image();
                    img.onload = () => {
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

                        // Final fallback: global app graph helper
                        if (app && app.graph && typeof app.graph.setDirtyCanvas === 'function') {
                            app.graph.setDirtyCanvas(true, true);
                        }
                    };
                    img.onerror = (e) => {
                        console.error('Failed to load image for mbImageShow', e);
                    };

                    img.src = `data:image/png;base64,${item.image_b64}`;
                }
            }
        };
    }
}

app.registerExtension({
    name: "Mockba.ImageShow",
    async beforeRegisterNodeDef(nodeType, nodeData, _app) {
        if (nodeData.name === "mbImageShow") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                if (onNodeCreated) onNodeCreated.apply(this, []);
                this.mbImageShow = new mbImageShow(this);
            };
        }
    }
});
