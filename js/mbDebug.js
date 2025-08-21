import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

class mbDebug {
    constructor(node) {
        this.node = node;
        this.node.properties = this.node.properties || {};
        
        // Initialize properties with defaults
        this.node.properties.console_output = this.node.properties.console_output ?? false;
        this.node.properties.truncate_size = this.node.properties.truncate_size ?? 500;

        // Create the debug output widget
        ComfyWidgets["STRING"](this.node, "debug_output", ["STRING", {
            multiline: true, 
            default: "Debug output will appear here after execution..."
        }], app);

        this.node.onConfigure = function() {
            // Called when loading from workflow - ensure properties are valid
            this.properties = this.properties || {};
            this.properties.console_output = this.properties.console_output ?? false;
            this.properties.truncate_size = this.properties.truncate_size ?? 500;
        };

        this.node.onGraphConfigured = function() {
            this.configured = true;
            this.onPropertyChanged();
        };

        this.node.onPropertyChanged = function(propName) {
            if (!this.configured) return;
            
            // Validate properties
            if (typeof this.properties.console_output !== 'boolean') {
                this.properties.console_output = false;
            }
            if (typeof this.properties.truncate_size !== 'number' || this.properties.truncate_size < 0 || this.properties.truncate_size > 10000) {
                this.properties.truncate_size = 500;
            }
        };

        // Handle execution output to update debug_output widget
        this.node.onExecuted = function (message) {
            if (this.widgets && message?.debug_output) {
                const debugWidget = this.widgets.find(w => w.name === "debug_output");
                if (debugWidget) {
                    debugWidget.value = message.debug_output[0];
                }
                this.onResize?.(this.size);
            }
        };
    }
}

// Register the extension
app.registerExtension({
    name: "Mockba.Debug",
    async beforeRegisterNodeDef(nodeType, nodeData, _app) {
        if (nodeData.name === "mbDebug") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                if (onNodeCreated) onNodeCreated.apply(this, []);
                this.mbDebug = new mbDebug(this);
            };
        }
    }
});
