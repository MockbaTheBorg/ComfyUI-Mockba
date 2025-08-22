import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

// Define default properties
const DEFAULT_MAX_LENGTH = 500;

class mbDisplay {
    constructor(node) {
        this.node = node;
        this.node.properties = this.node.properties || {};

        // Initialize properties with defaults
        this.node.properties.max_length = this.node.properties.max_length ?? DEFAULT_MAX_LENGTH;

        // Create the value display widget
        ComfyWidgets["STRING"](this.node, "value", ["STRING", {
            multiline: true,
            default: ""
        }], app);

        this.node.onConfigure = function () {
            // Called when loading from workflow - ensure properties are valid
            this.properties = this.properties || {};
            this.properties.max_length = this.properties.max_length ?? DEFAULT_MAX_LENGTH;
        };

        this.node.onGraphConfigured = function () {
            this.configured = true;
            this.onPropertyChanged();
        };

        this.node.onPropertyChanged = function (propName) {
            if (!this.configured) return;

            // Validate properties
            if (typeof this.properties.max_length !== 'number') {
                this.properties.max_length = DEFAULT_MAX_LENGTH;
            }
        };

        // Handle execution output to update value widget
        this.node.onExecuted = function (message) {
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
    name: "Mockba.Display",
    async beforeRegisterNodeDef(nodeType, nodeData, _app) {
        if (nodeData.name === "mbDisplay") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, []);
                this.mbDisplay = new mbDisplay(this);
            };
        }
    }
});
