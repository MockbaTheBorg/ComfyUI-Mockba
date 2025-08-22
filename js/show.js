import { app } from "../../scripts/app.js";

class mbImageShow {
    constructor(node) {
        this.node = node;

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

                                    // Return widget used width and height (system uses this to layout)
                                    return [widgetWidth, drawHeight + 10];
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
                        if (this.graph && this.graph.canvas) {
                            this.graph.canvas.setDirty(true);
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
