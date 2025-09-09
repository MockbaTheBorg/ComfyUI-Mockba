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

		// Helper function to add a callback to onDrawForeground
		const addNodeDrawForegroundHook = (callback) => {
			const onDrawForeground = nodeType.prototype.onDrawForeground;
			nodeType.prototype.onDrawForeground = function () {
				const r = onDrawForeground?.apply(this, arguments);
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
			case 'mbEval':
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
					// Hide the Queue Panel when mbSubmit is added
					const queuePanel = document.querySelector('div.p-panel-content');
					if (queuePanel) {
						queuePanel.style.display = 'none';
					}
					this.addWidget("button", "Submit Workflow", "Submit Workflow", () => app.queuePrompt(0));
			        this.addWidget("button", "Cancel Workflow", "Cancel Workflow", async () => {
			            try {
			                const response = await fetch('/api/interrupt', {
			                    method: 'POST',
			                    headers: {
			                        'Content-Type': 'application/json',
			                    }
			                });
			                if (response.ok) {
								app.extensionManager.toast.add({
								  severity: "info",
								  summary: "Information",
								  detail: "Workflow cancellation sent"
								});
			                } else {
								app.extensionManager.toast.add({
								  severity: "error",
								  summary: "Information",
								  detail: "Workflow cancellation failed"
								});
			                }
			            } catch (error) {
							app.extensionManager.toast.add({
							  severity: "error",
							  summary: "Information",
							  detail: "Workflow cancellation request failed"
							});
						}
			        });
					this.addWidget("button", "Reset Canvas", "Reset Canvas", () => {
						if (app.canvas) {
							app.canvas.ds.offset = [0, 0];
							app.canvas.ds.scale = 1;
							app.canvas.setDirty(true, true);
						}
					});
					this.size = [180, 55];
				});
				addNodeDrawForegroundHook(function () {
					this.size = [180, 55];
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

		// Manage nodes with dynamic inputs
		if (nodeData.name === 'mbImageBatch' ||
			nodeData.name === 'mbAudioCat' ||
			nodeData.name === 'mbSelect' ||
			nodeData.name === 'mbDemux' ||
			nodeData.name === 'mbEval' ||
			nodeData.name === 'mbExec') {

			// Name the dynamic inputs according to the node type
			var input_name = "input";
			switch (nodeData.name) {
				case 'mbImageBatch':
					input_name = "image";
					break;
				case 'mbAudioCat':
					input_name = "audio";
					break;
				case 'mbEval':
				case 'mbExec':
					input_name = "i";
					break;
			}

			// Handle connections change
			const onConnectionsChange = nodeType.prototype.onConnectionsChange;
			nodeType.prototype.onConnectionsChange = function (type, index, connected, link_info) {
				if (!link_info)
					return;

				// Only handle input connections
				if (type != 1)
					return;

				let select_slot = this.inputs.find(x => x.name == "select");
				let code_slot = this.inputs.find(x => x.name == "code");

				let converted_count = 0;
				converted_count += select_slot ? 1 : 0;
				converted_count += code_slot ? 1 : 0;

				if (!connected && (this.inputs.length > 1 + converted_count)) {
					const stackTrace = new Error().stack;

					// be defensive: ensure stackTrace is a string and the input at index exists
					const trace = stackTrace || "";
					const inputAtIndex = this.inputs[index];
					if (
						!trace.includes('LGraphNode.prototype.connect') && // for touch device
						!trace.includes('LGraphNode.connect') && // for mouse device
						!trace.includes('loadGraphData') &&
						inputAtIndex && inputAtIndex.name != 'select' && inputAtIndex.name != 'code') {
						// compute the last dynamic input index (skip 'select' and 'code')
						let lastDynamicIndex = -1;
						for (let i = this.inputs.length - 1; i >= 0; i--) {
							const inpt = this.inputs[i];
							if (inpt && inpt.name != 'select' && inpt.name != 'code') {
								lastDynamicIndex = i;
								break;
							}
						}
						// Only remove the input if it's the last dynamic slot. This prevents a disconnect
						// in the middle from collapsing subsequent inputs and losing their links.
						if (index === lastDynamicIndex) {
							this.removeInput(index);
						}
					}
				}


				// Enforce there is exactly one free dynamic input after the last connected input.
				// Build a list of dynamic inputs (skip 'select' and 'code') with their global indices.
				const dynamicEntries = [];
				for (let i = 0; i < this.inputs.length; i++) {
					const inp = this.inputs[i];
					if (!inp) continue;
					if (inp.name != 'select' && inp.name != 'code')
						dynamicEntries.push({ inp, idx: i });
				}

				// find last connected dynamic position (index into dynamicEntries)
				let lastConnectedPos = -1;
				for (let i = 0; i < dynamicEntries.length; i++) {
					if (dynamicEntries[i].inp.link != undefined) lastConnectedPos = i;
				}

				const desiredDynamicCount = Math.max(1, lastConnectedPos + 2); // one free after last connected
				const currentDynamicCount = dynamicEntries.length;

				if (currentDynamicCount > desiredDynamicCount) {
					// remove trailing dynamic inputs (from the end) until we reach desired count
					for (let i = currentDynamicCount - 1; i >= desiredDynamicCount; i--) {
						const globalIndex = dynamicEntries[i].idx;
						// double-check it's free before removing
						if (this.inputs[globalIndex] && this.inputs[globalIndex].link == undefined) {
							this.removeInput(globalIndex);
						}
					}
				} else if (currentDynamicCount < desiredDynamicCount) {
					// add missing inputs to reach desired count
					for (let i = 0; i < (desiredDynamicCount - currentDynamicCount); i++) {
						const outType = (this.outputs && this.outputs[0]) ? this.outputs[0].type : undefined;
						// only forward a concrete string type and avoid propagating '*' or non-strings
						if (typeof outType === 'string' && outType !== '*') {
							this.addInput(`${input_name}${currentDynamicCount + i + 1}`, outType);
						} else {
							this.addInput(`${input_name}${currentDynamicCount + i + 1}`);
						}
					}
				}

				// rename dynamic inputs sequentially
				let slot_i = 1;
				for (let i = 0; i < this.inputs.length; i++) {
					let input_i = this.inputs[i];
					if (input_i.name != 'select' && input_i.name != 'code') {
						input_i.name = `${input_name}${slot_i}`;
						slot_i++;
					}
				}

				// Adjust the 'select' widget range only for mbSelect nodes and only if the widget exists.
				if (nodeData.name == 'mbSelect') {
					if (this.widgets) {
						const selectWidget = this.widgets.find(w => w.name === 'select');
						if (selectWidget) {
							// Recompute the current dynamic inputs (after possible add/remove above)
							const currentDynamics = [];
							for (let i = 0; i < this.inputs.length; i++) {
								const inp = this.inputs[i];
								if (!inp) continue;
								if (inp.name != 'select' && inp.name != 'code') currentDynamics.push(inp);
							}

							let lastConnected = -1;
							for (let i = 0; i < currentDynamics.length; i++) {
								if (currentDynamics[i].link != undefined) lastConnected = i;
							}

							selectWidget.options = selectWidget.options || {};
							if (lastConnected === -1) {
								// no connected dynamic inputs -> select has no valid range
								selectWidget.options.min = 0;
								selectWidget.options.max = 0;
								selectWidget.value = 0;
							} else {
								// at least one connected input: min is 1, max is index-of-last-connected (1-based)
								selectWidget.options.min = 1;
								selectWidget.options.max = lastConnected + 1;
								// clamp current value into new range
								selectWidget.value = Math.min(Math.max(selectWidget.value || 0, selectWidget.options.min), selectWidget.options.max);
							}
						}
					}
				}

				// Resize the select widget
				if (!connected) {
					this.setSize(this.computeSize());
					this.setDirtyCanvas(true, true);
				}
			}
		}
	},
});
