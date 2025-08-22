import { app } from "../../scripts/app.js";

class mbEnd {
    constructor(node) {
        this.node = node;
        this.node.properties = this.node.properties || {};

        this.node.onAdded = function() {
            // Collapse the node by default
            this.flags = this.flags || {};
            this.flags.collapsed = true;
        };
    }
}

// Register the extension with ComfyUI
app.registerExtension({
    name: "Mockba.End",
    nodeCreated(node) {
        if (node.comfyClass === "mbEnd") {
            new mbEnd(node);
        }
    }
});
