import { app } from "../../scripts/app.js";
import { sprintf } from "./sprintf.js";

// Define the defaults
const DEFAULT_FORMAT = "";
const DEFAULT_SHOW_TYPE = false;
const DEFAULT_MAX_LENGTH = 25;

class mbValue {
    constructor(node) {
        this.node = node;
        this.node.properties = this.node.properties || {};
        
        // Initialize properties with defaults
        this.node.properties.format = this.node.properties.format || DEFAULT_FORMAT;
        this.node.properties.show_type = this.node.properties.show_type || DEFAULT_SHOW_TYPE;
        this.node.properties.max_length = this.node.properties.max_length || DEFAULT_MAX_LENGTH;

        this.node.onAdded = function() {
            // Collapse the node by default
            this.flags = this.flags || {};
            this.flags.collapsed = true;
        };

        this.node.onConfigure = function() {
            // Called when loading from workflow - ensure properties are valid
            this.properties = this.properties || {};
            this.properties.format = this.properties.format || DEFAULT_FORMAT;
            this.properties.show_type = this.properties.show_type || DEFAULT_SHOW_TYPE;
            this.properties.max_length = this.properties.max_length || DEFAULT_MAX_LENGTH;
        };

        this.node.onGraphConfigured = function() {
            this.configured = true;
            this.onPropertyChanged();
        };

        this.node.onPropertyChanged = function(propName) {
            if (!this.configured) return;
            
            // Validate properties
            if (typeof this.properties.format !== 'string') {
                this.properties.format = DEFAULT_FORMAT;
            }
            if (typeof this.properties.show_type !== 'boolean') {
                this.properties.show_type = DEFAULT_SHOW_TYPE;
            }
            if (typeof this.properties.max_length !== 'number') {
                this.properties.max_length = DEFAULT_MAX_LENGTH;
            }
        };

        // Handle execution output to update node title
        this.node.onExecuted = function(message) {
            if (message && message.value !== undefined) {
                const value = message.value[0];
                const format = this.properties.format || DEFAULT_FORMAT;
                const showType = this.properties.show_type || DEFAULT_SHOW_TYPE;
                const maxLength = this.properties.max_length || DEFAULT_MAX_LENGTH;

                let displayTitle = "Value";
                
                try {
                    if (typeof value === 'number') {
                        displayTitle = showType ? `${Number.isInteger(value) ? 'INT' : 'FLOAT'}: ${value}` : `${value}`;
                    } else if (typeof value === 'string') {
                        const displayStr = value.length > maxLength ? value.substring(0, maxLength) + "..." : value;
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
                    console.error("Error formatting value for mbValue node title:", e);
                }
                if (typeof value === 'number' || typeof value === 'string') {
                    if (format !== "") {
                        displayTitle = sprintf(format, displayTitle);
                    }
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
