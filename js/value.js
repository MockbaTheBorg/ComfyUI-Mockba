import { app } from "../../scripts/app.js";

class mbValue {
    constructor(node) {
        this.node = node;
        this.node.properties = this.node.properties || {};
        
        // Initialize properties with defaults
        this.node.properties.format = this.node.properties.format || "";
        this.node.properties.show_type = this.node.properties.show_type || false;

        // Hide the hidden inputs from the UI - check if widgets exist first
        if (this.node.widgets && this.node.widgets.length > 0) {
            for (let i = 0; i < this.node.widgets.length; i++) {
                const widget = this.node.widgets[i];
                if (widget.name === "format" || widget.name === "show_type") {
                    widget.hidden = true;
                    widget.type = "hidden";
                }
            }
        }

        this.node.onAdded = function() {
            // Collapse the node by default
            this.flags = this.flags || {};
            this.flags.collapsed = true;
            
            // Hide widgets when node is added
            if (this.widgets) {
                for (let i = 0; i < this.widgets.length; i++) {
                    const widget = this.widgets[i];
                    if (widget.name === "format" || widget.name === "show_type") {
                        widget.hidden = true;
                        widget.type = "hidden";
                    }
                }
            }
        };

        this.node.onConfigure = function() {
            // Called when loading from workflow - ensure properties are valid
            this.properties = this.properties || {};
            this.properties.format = this.properties.format || "";
            this.properties.show_type = this.properties.show_type || false;
        };

        this.node.onGraphConfigured = function() {
            this.configured = true;
            this.onPropertyChanged();
        };

        this.node.onPropertyChanged = function(propName) {
            if (!this.configured) return;
            
            // Validate properties
            if (typeof this.properties.format !== 'string') {
                this.properties.format = "";
            }
            if (typeof this.properties.show_type !== 'boolean') {
                this.properties.show_type = false;
            }

            // Update corresponding hidden widget values if widgets exist
            if (this.widgets) {
                for (let i = 0; i < this.widgets.length; i++) {
                    const widget = this.widgets[i];
                    if (widget.name === "format") {
                        widget.value = this.properties.format;
                    } else if (widget.name === "show_type") {
                        widget.value = this.properties.show_type;
                    }
                }
            }
        };

        // Handle execution output to update node title
        this.node.onExecuted = function(message) {
            if (message && message.value !== undefined) {
                const value = message.value[0];
                const showType = this.properties.show_type || false;
                let displayTitle = "Value";
                
                try {
                    if (typeof value === 'number') {
                        displayTitle = showType ? `${Number.isInteger(value) ? 'INT' : 'FLOAT'}: ${value}` : `${value}`;
                    } else if (typeof value === 'string') {
                        const displayStr = value.length > 25 ? value.substring(0, 25) + "..." : value;
                        displayTitle = showType ? `STRING: ${displayStr}` : displayStr;
                    } else if (Array.isArray(value)) {
                        displayTitle = showType ? `LIST: [${value.length} items]` : `[${value.length} items]`;
                    } else if (value && typeof value === 'object' && value.shape) {
                        displayTitle = showType ? `TENSOR: ${JSON.stringify(value.shape)}` : `${JSON.stringify(value.shape)}`;
                    } else if (typeof value === 'boolean') {
                        displayTitle = showType ? `BOOLEAN: ${value}` : `${value}`;
                    } else if (value === null) {
                        displayTitle = showType ? `NULL: null` : `null`;
                    } else if (value && typeof value === 'object') {
                        const typeName = value.constructor ? value.constructor.name : 'OBJECT';
                        displayTitle = showType ? `${typeName.toUpperCase()}: <object>` : `${value}`;
                    } else {
                        const typeName = typeof value;
                        displayTitle = showType ? `${typeName.toUpperCase()}: ${value}` : `${value}`;
                    }
                } catch (e) {
                    displayTitle = "UNKNOWN: <error>";
                }
                
                this.title = `${displayTitle}`;
                this.setDirtyCanvas(true, true);
            }
        };
    }
}

// Register the extension
app.registerExtension({
    name: "Mockba.Value",
    async beforeRegisterNodeDef(nodeType, nodeData, _app) {
        if (nodeData.name === "mbValue") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                if (onNodeCreated) onNodeCreated.apply(this, []);
                this.mbValue = new mbValue(this);
            };
        }
    }
});
