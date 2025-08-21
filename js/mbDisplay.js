import { app } from "../../scripts/app.js";

class mbDisplay {
    constructor(node) {
        this.node = node;
        this.node.properties = this.node.properties || {};
        
        // Initialize properties with defaults
        this.node.properties.console_output = this.node.properties.console_output ?? false;
        this.node.properties.truncate_size = this.node.properties.truncate_size ?? 500;

        // Hide the hidden inputs from the UI - check if widgets exist first
        if (this.node.widgets && this.node.widgets.length > 0) {
            for (let i = 0; i < this.node.widgets.length; i++) {
                const widget = this.node.widgets[i];
                if (widget.name === "console_output" || widget.name === "truncate_size") {
                    widget.hidden = true;
                    widget.type = "hidden";
                }
            }
        }

        this.node.onAdded = function() {
            // Hide widgets when node is added
            if (this.widgets) {
                for (let i = 0; i < this.widgets.length; i++) {
                    const widget = this.widgets[i];
                    if (widget.name === "console_output" || widget.name === "truncate_size") {
                        widget.hidden = true;
                        widget.type = "hidden";
                    }
                }
            }
        };

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

            // Update corresponding hidden widget values if widgets exist
            if (this.widgets) {
                for (let i = 0; i < this.widgets.length; i++) {
                    const widget = this.widgets[i];
                    if (widget.name === "console_output") {
                        widget.value = this.properties.console_output;
                    } else if (widget.name === "truncate_size") {
                        widget.value = this.properties.truncate_size;
                    }
                }
            }
        };

        // Handle execution output to update value widget
        this.node.onExecuted = function (message) {
            if (this.widgets && message?.value) {
                const newValue = message.value[0];
                
                const valueWidget = this.widgets.find(w => w.name === "value");
                if (valueWidget) {
                    valueWidget.value = newValue;
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
            nodeType.prototype.onNodeCreated = function() {
                if (onNodeCreated) onNodeCreated.apply(this, []);
                this.mbDisplay = new mbDisplay(this);
            };
        }
    }
});
