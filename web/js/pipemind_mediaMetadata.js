import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

// Shows the formatted metadata report on the PipemindMediaMetadata node.
app.registerExtension({
	name: "pipemind.MediaMetadata",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name !== "PipemindMediaMetadata") return;

		const REPORT = "metadata_report";

		function populate(text) {
			const report = Array.isArray(text) ? text.join("\n") : (text ?? "");

			let widget = this.widgets?.find((w) => w.name === REPORT);
			if (!widget) {
				widget = ComfyWidgets["STRING"](
					this,
					REPORT,
					["STRING", { multiline: true }],
					app
				).widget;
				widget.inputEl.readOnly = true;
				widget.inputEl.style.opacity = 0.8;
				widget.inputEl.style.fontFamily =
					"ui-monospace, SFMono-Regular, Menlo, Consolas, monospace";
				widget.inputEl.style.fontSize = "11px";
				widget.serializeValue = async () => widget.value;
			}
			widget.value = report;

			requestAnimationFrame(() => {
				const sz = this.computeSize();
				// Only ever grow, so a manual resize by the user is not undone.
				sz[0] = Math.max(sz[0], this.size[0], 400);
				sz[1] = Math.max(sz[1], this.size[1], 320);
				this.onResize?.(sz);
				app.graph.setDirtyCanvas(true, false);
			});
		}

		const onExecuted = nodeType.prototype.onExecuted;
		nodeType.prototype.onExecuted = function (message) {
			onExecuted?.apply(this, arguments);
			populate.call(this, message?.text);
		};

		// Widget values are stripped during configure on newer frontends, so
		// stash them first and restore the report once the node is built.
		const VALUES = Symbol();
		const configure = nodeType.prototype.configure;
		nodeType.prototype.configure = function () {
			this[VALUES] = arguments[0]?.widgets_values;
			return configure?.apply(this, arguments);
		};

		const onConfigure = nodeType.prototype.onConfigure;
		nodeType.prototype.onConfigure = function () {
			onConfigure?.apply(this, arguments);
			const values = this[VALUES];
			const saved = Array.isArray(values) ? values[values.length - 1] : undefined;
			if (typeof saved === "string" && saved.includes("Pipemind Media Metadata")) {
				requestAnimationFrame(() => populate.call(this, saved));
			}
		};
	},
});
