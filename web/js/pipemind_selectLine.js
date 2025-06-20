import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "pipemind.SelectLine.UI",

    beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData?.name !== "SelectLineFromDropdown") return;

        // Red overlay when disabled
        const originalDrawFG = nodeType.prototype.onDrawForeground;
        nodeType.prototype.onDrawForeground = function (ctx) {
            if (originalDrawFG) originalDrawFG.call(this, ctx);
            const enabledWidget = this.widgets?.find((w) => w.name === "enabled");
            const disabled = enabledWidget && enabledWidget.value === false;
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
    }
});