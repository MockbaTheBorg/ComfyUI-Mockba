import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

app.registerExtension({
	name: "Comfy.Mockba",

	beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "mb Textbox") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated?.apply(this, arguments);
				return r;
			};

			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);

				for (const widget of this.widgets) {
					if (widget.type === "customtext") {
						widget.value = message.text.join("");
					}
				}

				this.onResize?.(this.size);
			};
		}
		if (nodeData.name === "mb Debug") {
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);

				// Update debug output widget with execution results
				if (this.widgets && message?.debug_output) {
					const debugWidget = this.widgets.find(w => w.name === "debug_output");
					if (debugWidget) {
						debugWidget.value = message.debug_output[0];
					}
					this.onResize?.(this.size);
				}
			};
		}
		if (nodeData.name === 'mb Image Size') {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated?.apply(this, arguments);
				const iw = ComfyWidgets["INT"](this, "width", ["INT", {}], app).widget;
				const ih = ComfyWidgets["INT"](this, "height", ["INT", {}], app).widget;
				return r;
			};

			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);

				for (const widget of this.widgets) {
					if (widget.name == "width") {
						console.log(message);
						widget.value = message.width[0];
					}
					if (widget.name == "height") {
						console.log(message);
						widget.value = message.height[0];
					}
				}
				document.title = "executed";

				this.onResize?.(this.size);
			};
		}
		if (nodeData.name === 'mb Exec') {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated?.apply(this, arguments);
				
				// Helper functions for managing hidden state in code
				const HIDDEN_MARKER = "# __HIDDEN__";
				
				const isCodeHidden = (code) => {
					return code.startsWith(HIDDEN_MARKER);
				};
				
				const addHiddenMarker = (code) => {
					if (!isCodeHidden(code)) {
						return code ? HIDDEN_MARKER + "\n" + code : HIDDEN_MARKER;
					}
					return code;
				};
				
				const removeHiddenMarker = (code) => {
					if (isCodeHidden(code)) {
						return code.substring(HIDDEN_MARKER.length + 1); // +1 for the newline
					}
					return code;
				};
				
				// Add toggle button widget
				const toggleWidget = this.addWidget("button", "Hide Code", "Hide Code", () => {
					const codeWidget = this.widgets.find(w => w.name === "code");
					if (codeWidget) {
						if (codeWidget.type === "hidden") {
							// Show code widget
							codeWidget.type = "customtext";
							codeWidget.value = removeHiddenMarker(codeWidget.value);
							toggleWidget.name = "Hide Code";
							this.setSize(this.computeSize());
						} else {
							// Hide code widget
							codeWidget.type = "hidden";
							codeWidget.value = addHiddenMarker(codeWidget.value);
							toggleWidget.name = "Show Code";
							this.setSize(this.computeSize());
						}
						this.setDirtyCanvas(true, true);
					}
				});
				
				// Check initial state based on code content
				setTimeout(() => {
					const codeWidget = this.widgets.find(w => w.name === "code");
					if (codeWidget && isCodeHidden(codeWidget.value)) {
						// Code should be hidden initially
						codeWidget.type = "hidden";
						toggleWidget.name = "Show Code";
						this.setSize(this.computeSize());
						this.setDirtyCanvas(true, true);
					}
				}, 100);
				
				// Override serialize to maintain code widget functionality when hidden
				const originalSerialize = this.serialize;
				this.serialize = function() {
					const data = originalSerialize.apply(this, arguments);
					// Ensure code widget value is preserved even when hidden
					const codeWidget = this.widgets.find(w => w.name === "code");
					if (codeWidget && codeWidget.type === "hidden") {
						// Find the code widget in serialized data and ensure it's included
						if (data.widgets_values) {
							const codeIndex = this.widgets.findIndex(w => w.name === "code");
							if (codeIndex >= 0) {
								data.widgets_values[codeIndex] = codeWidget.value;
							}
						}
					}
					return data;
				};
				
				return r;
			};
		}
		if (nodeData.name === 'mb Image Batch' ||
			nodeData.name === 'mb Select' ||
			nodeData.name === 'mb Demux' ||
			nodeData.name === 'mb Eval' ||
			nodeData.name === 'mb Exec') {
			var input_name = "input";

			switch (nodeData.name) {
				case 'mb Image Batch':
					input_name = "image";
					break;
				case 'mb Eval':
				case 'mb Exec':
					input_name = "i";
					break;
			}

			const onConnectionsChange = nodeType.prototype.onConnectionsChange;
			nodeType.prototype.onConnectionsChange = function (type, index, connected, link_info) {
				if (!link_info)
					return;

				if (type == 2) {
					// connect output
					if (connected && index == 0) {
						if ((nodeData.name == 'mb Select' || nodeData.name == 'mb Demux') && app.graph._nodes_by_id[link_info.target_id]?.type == 'Reroute') {
							app.graph._nodes_by_id[link_info.target_id].disconnectInput(link_info.target_slot);
						}

						if (nodeData.name != 'mb Eval' && nodeData.name != 'mb Exec') {
							if (this.outputs[0].type == '*') {
								if (link_info.type == '*') {
									app.graph._nodes_by_id[link_info.target_id].disconnectInput(link_info.target_slot);
								}
								else {
									for (let i in this.inputs) {
										let input_i = this.inputs[i];
										if (input_i.name != 'select')
											input_i.type = link_info.type;
									}
									this.outputs[0].type = link_info.type;
									this.outputs[0].label = link_info.type;
									this.outputs[0].name = link_info.type;
								}
							}
						}
					}
					return;
				} else {
					// connect input
					if ((nodeData.name == 'mb Select' || nodeData.name == 'mb Demux') && app.graph._nodes_by_id[link_info.origin_id].type == 'Reroute')
						this.disconnectInput(link_info.target_slot);

					if (this.inputs[index].name == 'select' ||
						this.inputs[index].name == 'code')
						return;

					if (this.inputs[0].type == '*') {
						const node = app.graph.getNodeById(link_info.origin_id);
						let origin_type = node.outputs[link_info.origin_slot].type;

						if (nodeData.name != 'mb Eval' && nodeData.name != 'mb Exec') {
							if (origin_type == '*') {
								this.disconnectInput(link_info.target_slot);
								return;
							}
							for (let i in this.inputs) {
								let input_i = this.inputs[i];
								if (input_i.name != 'select')
									input_i.type = origin_type;
							}
							this.outputs[0].type = origin_type;
							this.outputs[0].label = origin_type;
							this.outputs[0].name = origin_type;
						}
					}
				}

				let select_slot = this.inputs.find(x => x.name == "select");
				let code_slot = this.inputs.find(x => x.name == "code");

				let converted_count = 0;
				converted_count += select_slot ? 1 : 0;
				converted_count += code_slot ? 1 : 0;

				if (!connected && (this.inputs.length > 1 + converted_count)) {
					const stackTrace = new Error().stack;

					if (
						!stackTrace.includes('LGraphNode.prototype.connect') && // for touch device
						!stackTrace.includes('LGraphNode.connect') && // for mouse device
						!stackTrace.includes('loadGraphData') &&
						this.inputs[index].name != 'select') {
						this.removeInput(index);
					}
				}

				let slot_i = 1;
				for (let i = 0; i < this.inputs.length; i++) {
					let input_i = this.inputs[i];
					if (input_i.name != 'select' && input_i.name != 'code') {
						input_i.name = `${input_name}${slot_i}`
						slot_i++;
					}
				}

				let last_slot = this.inputs[this.inputs.length - 1]; // last slot
				if (
					(last_slot.name == 'select' && this.inputs[this.inputs.length - 2].link != undefined) ||
					(last_slot.name == 'code' && this.inputs[this.inputs.length - 2].link != undefined) ||
					(last_slot.name != 'select' && last_slot.name != 'code' && last_slot.link != undefined)) {
					if (nodeData.name != 'mb Eval' && nodeData.name != 'mb Exec') {
						this.addInput(`${input_name}${slot_i}`, this.outputs[0].type);
					} else {
						this.addInput(`${input_name}${slot_i}`);
					}
				}

				if (nodeData.name == 'mb Select' || nodeData.name == 'mb Demux') {
					if (this.widgets) {
						this.widgets[0].options.max = select_slot ? this.inputs.length - 2 : this.inputs.length - 1;
						this.widgets[0].value = Math.min(this.widgets[0].value, this.widgets[0].options.max);
						if (this.widgets[0].options.max > 0 && this.widgets[0].value == 0)
							this.widgets[0].value = 1;
					}

				}
			}
		}
	},
});
