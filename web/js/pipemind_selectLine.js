import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "pipemind.SelectLine.UI",

    beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData?.name !== "SelectLineFromDropdown") return;

        // Helper function to get the effective enabled value
        function getEffectiveEnabledValue(node) {
            // Check if the enabled input is connected
            const enabledInput = node.inputs?.find(input => input.name === "enabled");
            if (enabledInput && enabledInput.link) {
                // If connected, get the value from the connected node
                const link = app.graph.links[enabledInput.link];
                if (link) {
                    const sourceNode = app.graph.getNodeById(link.origin_id);
                    if (sourceNode && sourceNode.outputs && sourceNode.outputs[link.origin_slot]) {
                        // Try to get the current output value
                        const outputValue = sourceNode.outputs[link.origin_slot].value;
                        if (outputValue !== undefined) {
                            return outputValue;
                        }
                        // Fallback: check if source node has a widget that might indicate the value
                        const sourceWidget = sourceNode.widgets?.find(w => w.name === "value" || w.name === "boolean");
                        if (sourceWidget) {
                            return sourceWidget.value;
                        }
                    }
                }
            }

            // If not connected or can't determine connected value, use widget value
            const enabledWidget = node.widgets?.find((w) => w.name === "enabled");
            return enabledWidget ? enabledWidget.value : true;
        }

        // Red overlay when disabled
        const originalDrawFG = nodeType.prototype.onDrawForeground;
        nodeType.prototype.onDrawForeground = function (ctx) {
            if (originalDrawFG) originalDrawFG.call(this, ctx);

            const effectiveEnabled = getEffectiveEnabledValue(this);
            const disabled = effectiveEnabled === false;

            if (!disabled) return;
            ctx.save();
            ctx.globalAlpha = 0.28;
            ctx.fillStyle = "#ff4d4d";
            if (typeof ctx.roundRect === "function") {
                ctx.roundRect(0, 0, this.size[0], this.size[1], 6);
                ctx.fill();
            } else {
                ctx.fillRect(0, 0, this.size[0], this.size[1]);
            }
            ctx.restore();
        };

        // Refresh when enabled toggles
        const originalWidgetChanged = nodeType.prototype.onWidgetChanged;
        nodeType.prototype.onWidgetChanged = function (widget, value, ...rest) {
            if (originalWidgetChanged) {
                originalWidgetChanged.call(this, widget, value, ...rest);
            }
            if (widget?.name === "enabled") {
                this.setDirtyCanvas(true, true);
            }
        };

        // Also refresh when connections change
        const originalOnConnectionsChange = nodeType.prototype.onConnectionsChange;
        nodeType.prototype.onConnectionsChange = function (type, index, connected, link_info, ...rest) {
            if (originalOnConnectionsChange) {
                originalOnConnectionsChange.call(this, type, index, connected, link_info, ...rest);
            }

            // If the enabled input connection changed, refresh the canvas
            if (type === 1 && this.inputs && this.inputs[index] && this.inputs[index].name === "enabled") {
                this.setDirtyCanvas(true, true);
            }
        };

        // Refresh when the graph is executed (to catch value changes from connected nodes)
        const originalOnExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message, ...rest) {
            if (originalOnExecuted) {
                originalOnExecuted.call(this, message, ...rest);
            }
            this.setDirtyCanvas(true, true);
        };
    }
});

