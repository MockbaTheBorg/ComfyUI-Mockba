import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

// Define default properties
const DEFAULT_MAX_LENGTH = 500;
const DEBUG = true; 0

// Local console log function to log messages only if debug mode is enabled
function logNodeEvent(eventName, node, ...args) {
    if (DEBUG) {
        console.log(`mbTest node ${eventName}:`, node, ...args);
    }
}

function truncateText(ctx, text, maxWidth, ellipsis = '...') {
    const textWidth = ctx.measureText(text).width

    if (textWidth <= maxWidth || maxWidth <= 0) {
        return text
    }

    const ellipsisWidth = ctx.measureText(ellipsis).width
    const availableWidth = maxWidth - ellipsisWidth

    if (availableWidth <= 0) {
        return ellipsis
    }

    // Binary search for the right length
    let low = 0
    let high = text.length
    let bestFit = 0

    while (low <= high) {
        const mid = Math.floor((low + high) / 2)
        const testText = text.substring(0, mid)
        const testWidth = ctx.measureText(testText).width

        if (testWidth <= availableWidth) {
            bestFit = mid
            low = mid + 1
        } else {
            high = mid - 1
        }
    }

    return text.substring(0, bestFit) + ellipsis
}


class mbTest {
    constructor(node) {
        this.node = node;
        this.node.properties = this.node.properties || {};

        // Create the value display widget
        ComfyWidgets["STRING"](this.node, "value", ["STRING", {
            multiline: true,
            default: " "
        }], app);

        this.node.onAdded = function (...args) {
            logNodeEvent("added", this, ...args);
        };

        this.node.onRemoved = function (...args) {
            logNodeEvent("removed", this, ...args);
        };

        this.node.onStart = function (...args) {
            logNodeEvent("started", this, ...args);
        };

        this.node.onStop = function (...args) {
            logNodeEvent("stopped", this, ...args);
        };

        //        this.node.onDrawForeground = function(...args) {
        //            logNodeEvent("draw foreground", this, ...args);
        //        };

        //        this.node.onDrawBackground = function(...args) {
        //            logNodeEvent("draw background", this, ...args);
        //        };

        this.node.onMouseDown = function (...args) {
            logNodeEvent("mouse down", this, ...args);
        };

        //        this.node.onMouseMove = function(...args) {
        //            logNodeEvent("mouse move", this, ...args);
        //        };

        this.node.onMouseUp = function (...args) {
            logNodeEvent("mouse up", this, ...args);
        };

        this.node.onMouseEnter = function (...args) {
            logNodeEvent("mouse enter", this, ...args);
        };

        this.node.onMouseLeave = function (...args) {
            logNodeEvent("mouse leave", this, ...args);
        };

        this.node.onKeyDown = function (...args) {
            logNodeEvent("key down", this, ...args);
        };

        this.node.onKeyUp = function (...args) {
            logNodeEvent("key up", this, ...args);
        };

        this.node.onExecute = function (...args) {
            logNodeEvent("execute", this, ...args);
        };

        this.node.onPropertyChanged = function (...args) {
            logNodeEvent("property changed", this, ...args);
            if (!this.configured) return;

            // Validate properties
            if (typeof this.properties.max_length !== 'number') {
                this.properties.max_length = DEFAULT_MAX_LENGTH;
            }
        };

        this.node.onGetInputs = function (...args) {
            logNodeEvent("get inputs", this, ...args);
        };

        this.node.onGetOutputs = function (...args) {
            logNodeEvent("get outputs", this, ...args);
        };

        //        this.node.onBounding = function(...args) {
        //            logNodeEvent("bounding", this, ...args);
        //        };

        this.node.onDblClick = function (...args) {
            logNodeEvent("dbl click", this, ...args);
        };

        this.node.onNodeTitleDblClick = function (...args) {
            logNodeEvent("node title dbl click", this, ...args);
        };

        this.node.onInputDblClick = function (...args) {
            logNodeEvent("input dbl click", this, ...args);
        };

        this.node.onOutputDblClick = function (...args) {
            logNodeEvent("output dbl click", this, ...args);
        };

        this.node.onConfigure = function (...args) {
            logNodeEvent("configure", this, ...args);
            // Called when loading from workflow - ensure properties are valid
            this.properties = this.properties || {};
        };

        this.node.onSerialize = function (...args) {
            logNodeEvent("serialize", this, ...args);
        };

        this.node.onSelected = function (...args) {
            logNodeEvent("selected", this, ...args);
        };

        this.node.onDeselected = function (...args) {
            logNodeEvent("deselected", this, ...args);
        };

        this.node.onDropItem = function (...args) {
            logNodeEvent("drop item", this, ...args);
        };

        this.node.onDropFile = function (...args) {
            logNodeEvent("drop file", this, ...args);
        };

        this.node.onBeforeConnectInput = function (...args) {
            logNodeEvent("before connect input", this, ...args);
        };

        this.node.onConnectInput = function (...args) {
            logNodeEvent("connect input", this, ...args);
        };

        this.node.onConnectOutput = function (...args) {
            logNodeEvent("connect output", this, ...args);
        };

        this.node.onConnectionsChange = function (...args) {
            logNodeEvent("connections changed", this, ...args);
        };

        this.node.onNodeInputAdd = function (...args) {
            logNodeEvent("node input added", this, ...args);
        };

        this.node.onNodeOutputAdd = function (...args) {
            logNodeEvent("node output added", this, ...args);
        };

        this.node.onInputAdded = function (...args) {
            logNodeEvent("input added", this, ...args);
        };

        this.node.onOutputAdded = function (...args) {
            logNodeEvent("output added", this, ...args);
        };

        this.node.onResize = function (...args) {
            logNodeEvent("resize", this, ...args);
        };

        this.node.onAction = function (...args) {
            logNodeEvent("action", this, ...args);
        };

        this.node.onGraphConfigured = function (...args) {
            logNodeEvent("graph configured", this, ...args);
            this.configured = true;
            this.onPropertyChanged();
        };

        this.node.updateOutputData = function (...args) {
            logNodeEvent("update output data", this, ...args);
        };

        this.node.onWidgetChanged = function (...args) {
            logNodeEvent("widget changed", this, ...args);
        };

        this.node.onDrawTitle = function (...args) {
            logNodeEvent("draw title", this, ...args);
        };

        this.node.onDrawTitleText = function (ctx, title_height, size, scale, title_text_font, selected, ...rest) {
            //logNodeEvent("draw title text", this, ctx, title_height, size, scale, title_text_font, selected, ...rest);
            ctx.font = this.titleFontStyle
            const rawTitle = this.getTitle() ?? `❌ ${this.type}`
            const title = String(rawTitle) + (this.pinned ? '📌' : '')
            if (title) {
                if (selected) {
                    ctx.fillStyle = LiteGraph.NODE_SELECTED_TITLE_COLOR
                } else {
                    ctx.fillStyle = this.constructor.title_text_color || "#FFF"
                }

                // Calculate available width for title
                let availableWidth = size[0] - title_height * 2 // Basic margins

                // Subtract space for title buttons
                if (this.title_buttons?.length > 0) {
                    let buttonsWidth = 0
                    const savedFont = ctx.font // Save current font
                    for (const button of this.title_buttons) {
                        if (button.visible) {
                            buttonsWidth += button.getWidth(ctx) + 2 // button width + gap
                        }
                    }
                    ctx.font = savedFont // Restore font after button measurements
                    if (buttonsWidth > 0) {
                        buttonsWidth += 10 // Extra margin before buttons
                        availableWidth -= buttonsWidth
                    }
                }

                // Truncate title if needed
                let displayTitle = title

                if (this.collapsed) {
                    // For collapsed nodes, limit to 20 chars as before
                    displayTitle = title.substr(0, 20)
                } else if (availableWidth > 0) {
                    // For regular nodes, truncate based on available width
                    displayTitle = truncateText(ctx, title, availableWidth)
                }

                ctx.textAlign = 'left'
                ctx.fillText(
                    displayTitle,
                    title_height,
                    LiteGraph.NODE_TITLE_TEXT_Y - title_height
                )
            }
        };

        this.node.onDrawTitleBox = function (ctx, title_height, size, scale) {
            //logNodeEvent("draw title box", this, ctx, title_height, size, scale);
            let box_size = 10;
            ctx.fillStyle = "rgba(100, 67, 33, 1)";
        ctx.beginPath()
        ctx.arc(
          title_height * 0.5,
          title_height * -0.5,
          box_size * 0.5,
          0,
          Math.PI * 2
        )
        ctx.fill()
       };

        this.node.onDrawTitleBar = function (ctx, title_height, size, scale, fgcolor) {
            //logNodeEvent("draw title bar", this, ctx, title_height, size, scale, fgcolor);
            fgcolor = "#852";
            if (this.collapsed) {
                ctx.shadowColor = LiteGraph.DEFAULT_SHADOW_COLOR
            }

            ctx.fillStyle = this.constructor.title_color || fgcolor
            ctx.beginPath()

            ctx.roundRect(
                0,
                -title_height,
                size[0],
                title_height,
                this.collapsed
                    ? [LiteGraph.ROUND_RADIUS]
                    : [LiteGraph.ROUND_RADIUS, LiteGraph.ROUND_RADIUS, 0, 0]
            )
            ctx.fill()
            ctx.shadowColor = 'transparent'
        };

        // Handle execution output to update value widget
        this.node.onExecuted = function (message) {
            logNodeEvent("executed", this, message);
            if (this.widgets && message?.value) {
                const newValue = message.value[0];

                const valueWidget = this.widgets.find(w => w.name === "value");
                if (valueWidget) {
                    const maxLength = this.properties.max_length || DEFAULT_MAX_LENGTH;
                    valueWidget.value = newValue.length > maxLength ? newValue.substring(0, maxLength) + "..." : newValue;
                }

                this.setDirtyCanvas(true, true);
            }
        };
    }
}

// Register the extension
app.registerExtension({
    name: "Mockba.Test",
    async beforeRegisterNodeDef(nodeType, nodeData, _app) {
        if (nodeData.name === "mbTest") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, []);
                this.mbTest = new mbTest(this);
            };
        }
    }
});
