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
		if (nodeData.name === "mb Display") {
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);

				// Update display output widget with execution results
				if (this.widgets && message?.value) {
					const newValue = message.value[0];
					const hasNewlines = newValue.includes('\n');
					
					// Find and properly remove the old widget
					const widgetIndex = this.widgets.findIndex(w => w.name === "value");
					if (widgetIndex >= 0) {
						const oldWidget = this.widgets[widgetIndex];
						
						// Properly dispose of the old widget's DOM elements
						if (oldWidget.inputEl && oldWidget.inputEl.parentNode) {
							oldWidget.inputEl.parentNode.removeChild(oldWidget.inputEl);
						}
						if (oldWidget.element && oldWidget.element.parentNode) {
							oldWidget.element.parentNode.removeChild(oldWidget.element);
						}
						
						// Remove from widgets array
						this.widgets.splice(widgetIndex, 1);
					}
					
					// Create new widget with correct multiline setting
					const newWidget = ComfyWidgets.STRING(this, "value", [
						"STRING", 
						{ multiline: hasNewlines, default: newValue }
					], app).widget;
					
					// Set the value
					newWidget.value = newValue;
					
					// Move widget to correct position if needed
					if (widgetIndex >= 0 && widgetIndex < this.widgets.length) {
						const widget = this.widgets.pop();
						this.widgets.splice(widgetIndex, 0, widget);
					}
					
					// Force node to recompute size and redraw
					this.setSize(this.computeSize());
					this.setDirtyCanvas(true, true);
					
					this.onResize?.(this.size);
				}
			};
		}
		if (nodeData.name === "mb Value") {
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);

				// Update node title based on the input value
				if (message && message.value !== undefined) {
					const value = message.value[0];
					let displayTitle = "Value";
					
					try {
						if (typeof value === 'number') {
							const valueType = Number.isInteger(value) ? 'INT' : 'FLOAT';
							displayTitle = `${valueType}: ${value}`;
						} else if (typeof value === 'string') {
							const displayStr = value.length > 25 ? value.substring(0, 25) + "..." : value;
							displayTitle = `STRING: ${displayStr}`;
						} else if (Array.isArray(value)) {
							displayTitle = `LIST: [${value.length} items]`;
						} else if (value && typeof value === 'object' && value.shape) {
							displayTitle = `TENSOR: ${JSON.stringify(value.shape)}`;
						} else if (typeof value === 'boolean') {
							displayTitle = `BOOLEAN: ${value}`;
						} else if (value === null) {
							displayTitle = `NULL: null`;
						} else if (value && typeof value === 'object') {
							const typeName = value.constructor ? value.constructor.name : 'OBJECT';
							displayTitle = `${typeName.toUpperCase()}: <object>`;
						} else {
							const typeName = typeof value;
							displayTitle = `${typeName.toUpperCase()}: ${value}`;
						}
					} catch (e) {
						displayTitle = "UNKNOWN: <error>";
					}
					
					this.title = displayTitle;
					this.setDirtyCanvas(true, true);
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
		if (nodeData.name === 'mb Submit') {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated?.apply(this, arguments);
				
				// Add submit button widget
				const submitWidget = this.addWidget("button", "Submit Workflow", "Submit Workflow", () => {
					// Queue the current workflow for execution
					app.queuePrompt(0); // 0 = add to end of queue, -1 = add to front
				});

				// Optional: Add a "Submit to Front" button for priority execution
				const submitFrontWidget = this.addWidget("button", "Submit to Front", "Submit to Front", () => {
					app.queuePrompt(-1); // -1 = add to front of queue
				});

				// Add reset canvas position button
				const resetCanvasWidget = this.addWidget("button", "Reset Canvas", "Reset Canvas", () => {
					// Reset canvas position to 0,0
					if (app.canvas) {
						app.canvas.ds.offset = [0, 0];
						app.canvas.ds.scale = 1;
						app.canvas.setDirty(true, true);
					}
				});

				return r;
			};
		}
		if (nodeData.name === "mb Color Mask") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated?.apply(this, arguments);
				
				// Add color picker button
				const pickColorButton = this.addWidget("button", "Pick Color", "Pick Color", () => {
					ColorPickerUtils.startColorPicking(this);
				});
				
				return r;
			};
		}
		if (nodeData.name === "mb Color Picker") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated?.apply(this, arguments);
				
				// Add color picker button
				const pickColorButton = this.addWidget("button", "Pick Color", "Pick Color", () => {
					ColorPickerUtils.startColorPicking(this);
				});
				
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
