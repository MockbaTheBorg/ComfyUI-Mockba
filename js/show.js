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
