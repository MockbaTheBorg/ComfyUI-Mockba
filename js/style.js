import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

// Default colors
const DEFAULT_SELECTED_COLOR = "#ffffffff";
const DEFAULT_TITLE_COLOR = "#ffffffb4";
const DEFAULT_BACKGROUND_COLOR = "#573d17ff";
const DEFAULT_BOX_COLOR = "#b8751dff";

// Truncate text to fit within a maximum width
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


class mbStyle {
    constructor(node) {
        this.node = node;

        this.node.onDrawTitleText = function (ctx, title_height, size, scale, title_text_font, selected, ...rest) {
            ctx.font = this.titleFontStyle
            const rawTitle = this.getTitle() ?? `❌ ${this.type}`
            const title = String(rawTitle) + (this.pinned ? '📌' : '')
            if (title) {
                if (selected) {
                    ctx.fillStyle = DEFAULT_SELECTED_COLOR
                } else {
                    ctx.fillStyle = DEFAULT_TITLE_COLOR
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
            let box_size = 10;
            ctx.fillStyle = DEFAULT_BOX_COLOR;

            // Center of the marker (kept the same as before)
            const cx = title_height * 0.5;
            const cy = title_height * -0.5;
            const half = box_size * 0.5;

            ctx.beginPath();
            if (this.collapsed) {
                // Small triangle pointing to the right
                ctx.moveTo(cx - half, cy - half);
                ctx.lineTo(cx - half, cy + half);
                ctx.lineTo(cx + half, cy);
            } else {
                // Small triangle pointing down
                ctx.moveTo(cx - half, cy - half);
                ctx.lineTo(cx + half, cy - half);
                ctx.lineTo(cx, cy + half);
            }
            ctx.closePath();
            ctx.fill();
        };

        this.node.onDrawTitleBar = function (ctx, title_height, size, scale, fgcolor) {
            fgcolor = DEFAULT_BACKGROUND_COLOR;
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
    }
}

// Register the extension
app.registerExtension({
    name: "Mockba.Style",
    async beforeRegisterNodeDef(nodeType, nodeData, _app) {
        if (typeof nodeData.name === "string" && /^mb[A-Z]/.test(nodeData.name)) {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, []);
                this.mbStyle = new mbStyle(this);
            };
        }
    }
});
