import { app } from "../../scripts/app.js";

// Dynamic Batch Input/Output nodes functionality
app.registerExtension({
	name: "Mockba.DynamicBatch",
	
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "mbBatchInput" || nodeData.name === "mbBatchOutput") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			
			nodeType.prototype.onNodeCreated = function() {
				const r = onNodeCreated?.apply(this, arguments);
				
				// Use a longer delay to ensure node is fully initialized
				setTimeout(() => {
					const configWidget = this.widgets?.find(w => w.name === "inputs" || w.name === "outputs");
					if (configWidget) {
						const originalCallback = configWidget.callback;
						configWidget.callback = (value) => {
							if (originalCallback) originalCallback(value);
							if (value > 0) this.setupDynamicConnections(value);
						};
						
						// Simple check: if value is -1, show popup after a delay to ensure we're not during loading
						if (configWidget.value === -1) {
							// Wait longer to ensure any workflow loading is complete
							setTimeout(() => {
								// Double-check the value hasn't changed (would indicate loading)
								if (configWidget.value === -1) {
									this.showConfigurationPopup();
								}
							}, 500);
						} else if (configWidget.value > 0) {
							this.setupDynamicConnections(configWidget.value);
						}
					}
				}, 100);
				
				return r;
			};
			
			nodeType.prototype.showConfigurationPopup = function() {
				const node = this;
				const isInput = nodeData.name === "mbBatchInput";
				const configField = isInput ? "inputs" : "outputs";
				
				const value = prompt(`How many ${configField} do you want? (2-16)`, "4");
				if (value === null) {
					app.graph.remove(node);
					return;
				}
				
				const count = parseInt(value);
				if (count >= 2 && count <= 16) {
					const configWidget = node.widgets?.find(w => w.name === configField);
					if (configWidget) {
						configWidget.value = count;
						node.setupDynamicConnections(count);
					}
				} else {
					alert("Please enter a value between 2 and 16");
					this.showConfigurationPopup();
				}
			};
			
			nodeType.prototype.setupDynamicConnections = function(count) {
				const isInput = nodeData.name === "mbBatchInput";
				
				if (isInput) {
					const currentCount = this.inputs.filter(input => input.name.startsWith("input_")).length;
					if (currentCount !== count) {
						// Remove existing dynamic inputs
						for (let i = this.inputs.length - 1; i >= 0; i--) {
							if (this.inputs[i].name.startsWith("input_")) {
								this.removeInput(i);
							}
						}
						// Add new inputs
						for (let i = 0; i < count; i++) {
							this.addInput(`input_${i+1}`, "*");
						}
					}
				} else {
					const currentCount = this.outputs.filter(output => output.name.startsWith("output_")).length;
					if (currentCount !== count) {
						// Remove existing dynamic outputs
						for (let i = this.outputs.length - 1; i >= 0; i--) {
							if (this.outputs[i].name.startsWith("output_")) {
								this.removeOutput(i);
							}
						}
						// Add new outputs
						for (let i = 0; i < count; i++) {
							this.addOutput(`output_${i+1}`, "*");
						}
					}
				}
				
				app.graph?.setDirtyCanvas(true, true);
			};
		}
	}
});
