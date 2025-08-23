import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

function node_info_copy(src, dest, connect_both, copy_shape) {
	// copy input connections
	for (let i in src.inputs) {
		let input = src.inputs[i];
		if (input.widget !== undefined) {
			const destWidget = dest.widgets.find(x => x.name === input.widget.name);
			dest.convertWidgetToInput(destWidget);
		}
		if (input.link) {
			let link = app.graph.links[input.link];
			let src_node = app.graph.getNodeById(link.origin_id);
			src_node.connect(link.origin_slot, dest.id, input.name);
		}
	}

	// copy output connections
	if (connect_both) {
		let output_links = {};
		for (let i in src.outputs) {
			let output = src.outputs[i];
			if (output.links) {
				let links = [];
				for (let j in output.links) {
					links.push(app.graph.links[output.links[j]]);
				}
				output_links[output.name] = links;
			}
		}

		for (let i in dest.outputs) {
			let links = output_links[dest.outputs[i].name];
			if (links) {
				for (let j in links) {
					let link = links[j];
					let target_node = app.graph.getNodeById(link.target_id);
					dest.connect(parseInt(i), target_node, link.target_slot);
				}
			}
		}
	}

	if (copy_shape) {
		dest.color = src.color;
		dest.bgcolor = src.bgcolor;
		dest.size = max(src.size, dest.size);
	}

	app.graph.afterChange();
}

// Shared color picking functionality for Mask from Color and Color Picker nodes
const ColorPickerUtils = {
	startColorPicking: function (node) {
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
					this.serialize = function () {
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
					this.size = [180, 55]; // Increased height to accommodate slider
				});
				addNodeDrawForegroundHook(function () {
					this.size = [180, 55]; // Updated size here too
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
				case 'mbEval':
				case 'mbExec':
					input_name = "i";
					break;
			}

			// Handle connections change
			nodeType.prototype.onConnectionsChange = function (type, index, connected, link_info) {
				if (!link_info)
					return;

				// type==1 -> Connecting an input
				if (type == 1) {
					// Do not trigger the dynamic process for 'select' and 'code' inputs
					if (this.inputs[index].name == 'select' ||
						this.inputs[index].name == 'code')
						return;

					// If the input type is '*', set it to the origin type
					if (this.inputs[index].type == '*') {
						const origin_node = app.graph.getNodeById(link_info.origin_id);
						let origin_type = origin_node.outputs[link_info.origin_slot].type;
						this.inputs[index].type = origin_type;
					}
				}

				// find the slots of the 'select' and 'code' inputs
				let select_slot = this.inputs.find(x => x.name == "select");
				let code_slot = this.inputs.find(x => x.name == "code");

				// Count the number of extra inputs
				let extra_inputs = 0;
				extra_inputs += select_slot ? 1 : 0;
				extra_inputs += code_slot ? 1 : 0;

				// !connected = Is disconnecting
				if (!connected && (this.inputs.length > 1 + extra_inputs)) {
					const stackTrace = new Error().stack;

					if (
						!stackTrace.includes('LGraphNode.prototype.connect') && // for touch device
						!stackTrace.includes('LGraphNode.connect') && // for mouse device
						!stackTrace.includes('loadGraphData') &&
						this.inputs[index].name != 'select' &&
						this.inputs[index].name != 'code'
					) {
						this.removeInput(index);
					}
				}

				// Rename the dynamic inputs
				let slot_i = 1;
				for (let i = 0; i < this.inputs.length; i++) {
					let input_i = this.inputs[i];
					if (input_i.name != 'select' && input_i.name != 'code') {
						input_i.name = `${input_name}${slot_i}`
						slot_i++;
					}
				}

				// Create a new empty last slot
				let last_slot = this.inputs[this.inputs.length - 1]; // select the last slot
				if (
					(last_slot.name == 'select' && this.inputs[this.inputs.length - 2].link != undefined) ||
					(last_slot.name == 'code' && this.inputs[this.inputs.length - 2].link != undefined) ||
					(last_slot.name != 'select' && last_slot.name != 'code' && last_slot.link != undefined)) {
					if (nodeData.name == 'mbImageBatch') {
						this.addInput(`${input_name}${slot_i}`, 'IMAGE');
					} else {
						this.addInput(`${input_name}${slot_i}`);
					}
				}

				// Fix the limits of the select widget: locate it by name, ensure min=1 and max=dynamic inputs
				if (nodeData.name == 'mbSelect') {
					if (this.widgets) {
						const selectWidget = this.widgets.find(w => w.name === 'select');
						if (selectWidget) {
							// Number of selectable dynamic inputs (exclude trailing special slots)
							const dynamicCount = select_slot ? this.inputs.length - 2 : this.inputs.length - 1;
							selectWidget.options = selectWidget.options || {};
							selectWidget.options.min = 1; // always enforce minimum 1
							selectWidget.options.max = Math.max(0, dynamicCount);
							// Clamp the current value between min and max when possible
							if (selectWidget.options.max >= selectWidget.options.min) {
								selectWidget.value = Math.min(Math.max(selectWidget.value || 0, selectWidget.options.min), selectWidget.options.max);
							} else {
								// no selectable inputs -> set value to 0 to indicate 'none'
								selectWidget.value = 0;
							}
						}
					}
				}

				// If disconnecting, recreate the node to recover its previous size
				if (!connected) {
					if (this.title != "dead") {
						let new_node = LiteGraph.createNode(nodeType.comfyClass);
						new_node.pos = [this.pos[0], this.pos[1]];
						app.canvas.graph.add(new_node, false);
						let prevTitle = this.title;
						this.title = "dead";
						node_info_copy(this, new_node, true);
						new_node.title = prevTitle;
						app.canvas.graph.remove(this);
					}
					requestAnimationFrame(() => app.canvas.setDirty(true, true))
				}
			}
		}
	},
});
