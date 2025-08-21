import { app } from "../../scripts/app.js";

class mbSignal {
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
    name: "mockba.signal",
    nodeCreated(node) {
        if (node.comfyClass === "mbSignal") {
            new mbSignal(node);
        }
    }
});
