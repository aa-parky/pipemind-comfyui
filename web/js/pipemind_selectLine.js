import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "pipemind.SelectLine",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "SelectLineFromDropdown") {
            console.log("Applying styling to SelectLineFromDropdown node");

            // Store the original onDrawForeground method
            const onDrawForeground = nodeType.prototype.onDrawForeground;

            // Override the onDrawForeground method
            nodeType.prototype.onDrawForeground = function(ctx) {
                // Call original method first if it exists
                if (onDrawForeground) {
                    onDrawForeground.apply(this, arguments);
                }

                // Apply red styling when node is disabled
                if (this.widgets && this.widgets.length > 0) {
                    const enabledWidget = this.widgets[0]; // The first widget should be 'enabled'
                    if (enabledWidget && enabledWidget.name === "enabled" && enabledWidget.value === false) {
                        // Save original box color if not saved
                        if (!this._originalBoxColor) {
                            this._originalBoxColor = this.boxcolor || "#000";
                        }

                        // Apply red title bar (this is the header part of the node)
                        ctx.fillStyle = "#991111";
                        ctx.beginPath();
                        ctx.rect(
                            0, 
                            0, 
                            this.size[0], 
                            LiteGraph.NODE_TITLE_HEIGHT
                        );
                        ctx.fill();

                        // Apply a red border around the node
                        ctx.strokeStyle = "#ff0000";
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        ctx.rect(
                            0, 
                            0, 
                            this.size[0], 
                            this.size[1]
                        );
                        ctx.stroke();

                        // Re-draw the title text with white color for better visibility
                        if (this.title) {
                            ctx.fillStyle = "#ffffff";
                            ctx.font = "bold 14px Arial";
                            ctx.textAlign = "center";
                            ctx.fillText(
                                this.title, 
                                this.size[0] / 2, 
                                LiteGraph.NODE_TITLE_HEIGHT * 0.7
                            );
                        }
                    } else if (this._originalBoxColor) {
                        // Restore original color if needed (not actually needed since redraw happens anyway)
                        delete this._originalBoxColor;
                    }
                }
            };

            // Override the onWidgetChanged method to force redraw when 'enabled' changes
            const onWidgetChanged = nodeType.prototype.onWidgetChanged;
            nodeType.prototype.onWidgetChanged = function(widget, value) {
                // Call original method if it exists
                if (onWidgetChanged) {
                    onWidgetChanged.apply(this, arguments);
                }

                // Force redraw when the enabled widget changes
                if (widget && widget.name === "enabled") {
                    this.setDirtyCanvas(true, true);
                }
            };
        }
    }
});
