import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

// Shared color picking functionality for Mask from Color and Color Picker nodes
const ColorPickerUtils = {
	startColorPicking: function(node) {
		// Create variables to store references for proper cleanup
		let isPickingActive = true;
		
		// Change cursor to indicate picking mode - use a more aggressive approach
		const originalBodyCursor = document.body.style.cursor;
		const originalDocumentCursor = document.documentElement.style.cursor;
		document.body.style.cursor = 'crosshair !important';
		document.documentElement.style.cursor = 'crosshair !important';
		
		// Add a global style to override all cursor styles during picking
		const cursorStyle = document.createElement('style');
		cursorStyle.textContent = '* { cursor: crosshair !important; }';
		document.head.appendChild(cursorStyle);
		
		// Find all image elements in the page (ComfyUI image previews)
		const imageElements = document.querySelectorAll('img, canvas');
		const originalPointerEvents = [];
		
		// Store original pointer events and make images clickable
		imageElements.forEach((img, index) => {
			originalPointerEvents[index] = img.style.pointerEvents;
			img.style.pointerEvents = 'auto';
		});
		
		// Create a temporary canvas for color sampling
		const tempCanvas = document.createElement('canvas');
		const tempCtx = tempCanvas.getContext('2d');
		
		const pickColor = (event) => {
			if (!isPickingActive) return;
			
			const target = event.target;
			
			// Check if clicked on an image or canvas
			if (target.tagName === 'IMG' || target.tagName === 'CANVAS') {
				event.preventDefault();
				event.stopPropagation();
				
				let imageData;
				let x, y;
				
				if (target.tagName === 'IMG') {
					// For IMG elements, draw to temporary canvas and sample
					const rect = target.getBoundingClientRect();
					x = Math.floor((event.clientX - rect.left) * (target.naturalWidth / rect.width));
					y = Math.floor((event.clientY - rect.top) * (target.naturalHeight / rect.height));
					
					tempCanvas.width = target.naturalWidth;
					tempCanvas.height = target.naturalHeight;
					tempCtx.drawImage(target, 0, 0);
					imageData = tempCtx.getImageData(x, y, 1, 1);
				} else if (target.tagName === 'CANVAS') {
					// For CANVAS elements, sample directly
					const rect = target.getBoundingClientRect();
					x = Math.floor((event.clientX - rect.left) * (target.width / rect.width));
					y = Math.floor((event.clientY - rect.top) * (target.height / rect.height));
					
					const ctx = target.getContext('2d');
					imageData = ctx.getImageData(x, y, 1, 1);
				}
				
				if (imageData) {
					const data = imageData.data;
					const r = data[0];
					const g = data[1];
					const b = data[2];
					const hexColor = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
					
					// Update color widget
					const colorWidget = node.widgets.find(w => w.name === "color");
					if (colorWidget) {
						colorWidget.value = hexColor;
						node.setDirtyCanvas(true, true);
					}
					
					// Clean up immediately after successful color pick
					stopColorPicking();
					return; // Exit the function to prevent further processing
				}
			}
			
			// If we clicked on something that's not an image/canvas, also stop picking
			stopColorPicking();
		};
		
		const cancelPicking = (event) => {
			if (event.key === 'Escape') {
				stopColorPicking();
			}
		};
		
		// Centralized cleanup function
		const stopColorPicking = () => {
			if (!isPickingActive) return;
			isPickingActive = false;
			
			// Remove global cursor style
			if (cursorStyle.parentNode) {
				cursorStyle.parentNode.removeChild(cursorStyle);
			}
			
			// Restore original cursors
			document.body.style.cursor = originalBodyCursor;
			document.documentElement.style.cursor = originalDocumentCursor;
			
			// Restore original pointer events
			imageElements.forEach((img, index) => {
				img.style.pointerEvents = originalPointerEvents[index];
			});
			
			// Remove all event listeners
			document.removeEventListener('click', pickColor, true);
			document.removeEventListener('keydown', cancelPicking);
		};
		
		// Add event listeners - delay to avoid catching the button click
		setTimeout(() => {
			if (isPickingActive) {
				document.addEventListener('click', pickColor, true);
				document.addEventListener('keydown', cancelPicking);
			}
		}, 100); // Small delay to let the button click finish
	}
};

app.registerExtension({
	name: "Mockba.Common",

	beforeRegisterNodeDef(nodeType, nodeData, app) {
		// Helper function to add a callback to onNodeCreated
		const addNodeCreatedHook = (callback) => {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated?.apply(this, arguments);
				callback.apply(this, arguments);
				return r;
			};
		};

		// Helper function to add a callback to onExecuted
		const addNodeExecutedHook = (callback) => {
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);
				callback.call(this, message);
			};
		};

		switch (nodeData.name) {
			case "mbTextbox":
				addNodeExecutedHook(function (message) {
					for (const widget of this.widgets) {
						if (widget.type === "customtext") {
							widget.value = message.text.join("");
						}
					}
					this.onResize?.(this.size);
				});
				break;
			case "mbDebug":
				addNodeExecutedHook(function (message) {
					if (this.widgets && message?.debug_output) {
						const debugWidget = this.widgets.find(w => w.name === "debug_output");
						if (debugWidget) {
							debugWidget.value = message.debug_output[0];
						}
						this.onResize?.(this.size);
					}
				});
				break;
			case "mbDisplay":
				addNodeExecutedHook(function (message) {
					if (this.widgets && message?.value) {
						const newValue = message.value[0];
						
						const valueWidget = this.widgets.find(w => w.name === "value");
						if (valueWidget) {
							valueWidget.value = newValue;
						}
						
						this.setDirtyCanvas(true, true);
					}
				});
				break;
			case "mbValue":
				addNodeCreatedHook(function () {
					const showTypeWidget = this.widgets?.find(w => w.name === "show_type");
					if (showTypeWidget) {
						const originalCallback = showTypeWidget.callback;
						showTypeWidget.callback = (value) => {
							if (originalCallback) {
								originalCallback.apply(this, arguments);
							}
							this.parent?.setDirtyCanvas(true, true);
						};
					}
				});
				addNodeExecutedHook(function (message) {
					if (message && message.value !== undefined) {
						const value = message.value[0];
						const showTypeWidget = this.widgets?.find(w => w.name === "show_type");
						const showType = showTypeWidget ? showTypeWidget.value : false;
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
				});
				break;
			case 'mbImageSize':
				addNodeCreatedHook(function () {
					ComfyWidgets["INT"](this, "width", ["INT", {}], app);
					ComfyWidgets["INT"](this, "height", ["INT", {}], app);
				});
				addNodeExecutedHook(function (message) {
					for (const widget of this.widgets) {
						if (widget.name === "width") {
							widget.value = message.width[0];
						}
						if (widget.name === "height") {
							widget.value = message.height[0];
						}
					}
					this.onResize?.(this.size);
				});
				break;
			case 'mbExec':
				addNodeCreatedHook(function () {
					const HIDDEN_MARKER = "# __HIDDEN__";
					const isCodeHidden = (code) => code.startsWith(HIDDEN_MARKER);
					const addHiddenMarker = (code) => !isCodeHidden(code) ? (code ? HIDDEN_MARKER + "\n" + code : HIDDEN_MARKER) : code;
					const removeHiddenMarker = (code) => isCodeHidden(code) ? code.substring(HIDDEN_MARKER.length + 1) : code;

					const toggleWidget = this.addWidget("button", "Hide Code", "Hide Code", () => {
						const codeWidget = this.widgets.find(w => w.name === "code");
						if (codeWidget) {
							if (codeWidget.type === "hidden") {
								codeWidget.type = "customtext";
								codeWidget.value = removeHiddenMarker(codeWidget.value);
								toggleWidget.name = "Hide Code";
							} else {
								codeWidget.type = "hidden";
								codeWidget.value = addHiddenMarker(codeWidget.value);
								toggleWidget.name = "Show Code";
							}
							this.setSize(this.computeSize());
							this.setDirtyCanvas(true, true);
						}
					});

					setTimeout(() => {
						const codeWidget = this.widgets.find(w => w.name === "code");
						if (codeWidget && isCodeHidden(codeWidget.value)) {
							codeWidget.type = "hidden";
							toggleWidget.name = "Show Code";
							this.setSize(this.computeSize());
							this.setDirtyCanvas(true, true);
						}
					}, 100);

					const originalSerialize = this.serialize;
					this.serialize = function() {
						const data = originalSerialize.apply(this, arguments);
						const codeWidget = this.widgets.find(w => w.name === "code");
						if (codeWidget && codeWidget.type === "hidden" && data.widgets_values) {
							const codeIndex = this.widgets.findIndex(w => w.name === "code");
							if (codeIndex >= 0) {
								data.widgets_values[codeIndex] = codeWidget.value;
							}
						}
						return data;
					};
				});
				break;
			case 'mbSubmit':
				addNodeCreatedHook(function () {
					this.addWidget("button", "Submit Workflow", "Submit Workflow", () => app.queuePrompt(0));
					this.addWidget("button", "Reset Canvas", "Reset Canvas", () => {
						if (app.canvas) {
							app.canvas.ds.offset = [0, 0];
							app.canvas.ds.scale = 1;
							app.canvas.setDirty(true, true);
						}
					});
				});
				break;
			case "mbColorPicker":
			case "mbMaskFromColor":
				addNodeCreatedHook(function () {
					this.addWidget("button", "Pick Color", "Pick Color", () => {
						ColorPickerUtils.startColorPicking(this);
					});
				});
				break;
		}
		if (nodeData.name === 'mbImageBatch' ||
			nodeData.name === 'mbSelect' ||
			nodeData.name === 'mbDemux' ||
			nodeData.name === 'mbEval' ||
			nodeData.name === 'mbExec') {
			var input_name = "input";

			switch (nodeData.name) {
				case 'mbImageBatch':
					input_name = "image";
					break;
				case 'mbEval':
				case 'mbExec':
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
						if ((nodeData.name == 'mbSelect' || nodeData.name == 'mbDemux') && app.graph._nodes_by_id[link_info.target_id]?.type == 'Reroute') {
							app.graph._nodes_by_id[link_info.target_id].disconnectInput(link_info.target_slot);
						}

						if (nodeData.name != 'mbEval' && nodeData.name != 'mbExec') {
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
					if ((nodeData.name == 'mbSelect' || nodeData.name == 'mbDemux') && app.graph._nodes_by_id[link_info.origin_id].type == 'Reroute')
						this.disconnectInput(link_info.target_slot);

					if (this.inputs[index].name == 'select' ||
						this.inputs[index].name == 'code')
						return;

					if (this.inputs[0].type == '*') {
						const node = app.graph.getNodeById(link_info.origin_id);
						let origin_type = node.outputs[link_info.origin_slot].type;

						if (nodeData.name != 'mbEval' && nodeData.name != 'mbExec') {
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
					if (nodeData.name != 'mbEval' && nodeData.name != 'mbExec') {
						this.addInput(`${input_name}${slot_i}`, this.outputs[0].type);
					} else {
						this.addInput(`${input_name}${slot_i}`);
					}
				}

				if (nodeData.name == 'mbSelect' || nodeData.name == 'mbDemux') {
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

// Dynamic Batch Input/Output nodes functionality
app.registerExtension({
	name: "Mockba.DynamicBatch",
	
	setup() {
		// Track when we're loading a workflow
		this.isLoadingWorkflow = false;
		
		const originalLoadGraphData = app.loadGraphData;
		app.loadGraphData = (graphData) => {
			this.isLoadingWorkflow = true;
			const result = originalLoadGraphData.call(app, graphData);
			// Reset the flag after a delay to allow all nodes to be created
			setTimeout(() => {
				this.isLoadingWorkflow = false;
			}, 100);
			return result;
		};
	},
	
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "mbBatchInput" || nodeData.name === "mbBatchOutput") {
			const extension = this;
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			
			nodeType.prototype.onNodeCreated = function() {
				const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
				
				// Set up widget callback and initial configuration check
				setTimeout(() => {
					const configWidget = this.widgets?.find(w => w.name === "inputs" || w.name === "outputs");
					if (configWidget) {
						// Setup widget callback for future changes
						const originalCallback = configWidget.callback;
						configWidget.callback = (value) => {
							if (originalCallback) originalCallback(value);
							if (value > 0) {
								this.setupDynamicConnections(value);
							}
						};
						
						// Only show popup if we're NOT loading a workflow and the value is -1
						if (!extension.isLoadingWorkflow && configWidget.value === -1) {
							this.showConfigurationPopup();
						} else if (configWidget.value > 0) {
							// Node is configured, set up dynamic connections
							this.setupDynamicConnections(configWidget.value);
						}
					}
				}, 50);
				
				return r;
			};
			
			// Add method to show configuration popup
			nodeType.prototype.showConfigurationPopup = function() {
				const node = this;
				const isInput = nodeData.name === "mbBatchInput";
				const configField = isInput ? "inputs" : "outputs";
				const label = isInput ? "inputs" : "outputs";
				
				// Create popup dialog
				const dialog = document.createElement("div");
				dialog.style.cssText = `
					position: fixed;
					top: 50%;
					left: 50%;
					transform: translate(-50%, -50%);
					background: #2a2a2a;
					border: 1px solid #555;
					border-radius: 8px;
					padding: 20px;
					z-index: 10000;
					color: white;
					font-family: Arial, sans-serif;
					box-shadow: 0 4px 12px rgba(0,0,0,0.5);
				`;
				
				dialog.innerHTML = `
					<h3 style="margin-top: 0;">Configure ${isInput ? 'Batch Input' : 'Batch Output'}</h3>
					<p>How many ${label} do you want?</p>
					<input type="number" id="configValue" min="2" max="16" value="4" style="
						width: 100px;
						padding: 5px;
						margin: 10px 0;
						background: #1a1a1a;
						border: 1px solid #555;
						color: white;
						border-radius: 4px;
					">
					<div style="margin-top: 15px;">
						<button id="configOk" style="
							background: #007acc;
							color: white;
							border: none;
							padding: 8px 16px;
							margin-right: 10px;
							border-radius: 4px;
							cursor: pointer;
						">OK</button>
						<button id="configCancel" style="
							background: #666;
							color: white;
							border: none;
							padding: 8px 16px;
							border-radius: 4px;
							cursor: pointer;
						">Cancel</button>
					</div>
				`;
				
				// Create backdrop
				const backdrop = document.createElement("div");
				backdrop.style.cssText = `
					position: fixed;
					top: 0;
					left: 0;
					width: 100%;
					height: 100%;
					background: rgba(0,0,0,0.5);
					z-index: 9999;
				`;
				
				document.body.appendChild(backdrop);
				document.body.appendChild(dialog);
				
				const input = dialog.querySelector("#configValue");
				const okBtn = dialog.querySelector("#configOk");
				const cancelBtn = dialog.querySelector("#configCancel");
				
				input.focus();
				input.select();
				
				const cleanup = () => {
					document.body.removeChild(backdrop);
					document.body.removeChild(dialog);
				};
				
				const confirm = () => {
					const value = parseInt(input.value);
					if (value >= 2 && value <= 16) {
						// Update the widget value
						const configWidget = node.widgets?.find(w => w.name === configField);
						if (configWidget) {
							configWidget.value = value;
							node.setupDynamicConnections(value);
						}
						cleanup();
					} else {
						alert("Please enter a value between 2 and 16");
					}
				};
				
				okBtn.onclick = confirm;
				cancelBtn.onclick = () => {
					// If cancelled, remove the node
					app.graph.remove(node);
					cleanup();
				};
				
				input.onkeydown = (e) => {
					if (e.key === "Enter") confirm();
					if (e.key === "Escape") cancelBtn.click();
				};
				
				backdrop.onclick = cancelBtn.onclick;
			};
			
			// Add method to setup dynamic connections
			nodeType.prototype.setupDynamicConnections = function(count) {
				const isInput = nodeData.name === "mbBatchInput";
				
				if (isInput) {
					// Setup dynamic inputs for mbBatchInput
					// Count current dynamic inputs
					const currentDynamicInputs = this.inputs.filter(input => 
						input.name.startsWith("input_")).length;
					
					// Only modify if the count is different
					if (currentDynamicInputs !== count) {
						// Remove existing optional inputs
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
					// Setup dynamic outputs for mbBatchOutput
					// Count current dynamic outputs
					const currentDynamicOutputs = this.outputs.filter(output => 
						output.name.startsWith("output_")).length;
					
					// Only modify if the count is different
					if (currentDynamicOutputs !== count) {
						// Store connections before removing outputs
						const connections = [];
						for (let i = 0; i < this.outputs.length; i++) {
							if (this.outputs[i].name.startsWith("output_") && this.outputs[i].links) {
								connections[i] = [...this.outputs[i].links];
							}
						}
						
						// Remove existing outputs
						for (let i = this.outputs.length - 1; i >= 0; i--) {
							if (this.outputs[i].name.startsWith("output_")) {
								this.removeOutput(i);
							}
						}
						
						// Add new outputs
						for (let i = 0; i < count; i++) {
							this.addOutput(`output_${i+1}`, "*");
						}
						
						// Restore connections that are still valid
						setTimeout(() => {
							for (let i = 0; i < connections.length && i < this.outputs.length; i++) {
								if (connections[i] && this.outputs[i]) {
									// ComfyUI will automatically reconnect valid links
								}
							}
						}, 10);
					}
				}
				
				// Trigger graph update
				if (app.graph) {
					app.graph.setDirtyCanvas(true, true);
				}
			};
		}
	}
});
