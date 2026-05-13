frappe.pages["gpf-builder"].on_page_load = function(wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "GPF Print Format Builder",
		single_column: true
	});

	$(frappe.render_template("gpf_builder", {})).appendTo(page.main);

	frappe.require([
		"/assets/gpf_builder/js/lib/konva.min.js",
		"/assets/gpf_builder/js/lib/pdf.min.js"
	], () => {
		pdfjsLib.GlobalWorkerOptions.workerSrc = "/assets/gpf_builder/js/lib/pdf.worker.min.js";
		window.gpf_builder_instance = new GPFBuilder();
	});

	class GPFBuilder {
		constructor() {
			this.setup = null;
			this.fields = [];
			this.ocr_results = [];
			this.source_docname = "";
			this.source_values = {};
			this.source_doc_control = null;
			this.stage = null;
			this.bg_layer = null;
			this.layer = null;
			this.transformer = null;
			this.selected_node = null;
			this.page_width = 800;
			this.page_height = Math.round(this.page_width * 1.414);
			this.init();
		}

		async init() {
			await this.fetch_setup();
			await this.fetch_fields();
			await this.fetch_ocr_results();
			this.init_stage();
			this.init_events();
			this.init_source_doc_control();
			this.render_field_list();
			this.render_ocr_results();
			await this.load_blocks();
			await this.render_pdf_background();
			this.refresh_status();
			this.apply_state_locking();
		}

		async call(method, args) {
			const response = await frappe.call({ method, args: args || {} });
			return response.message;
		}

		async fetch_setup() {
			this.setup = await this.call("gpf_builder.api.api.get_active_setup_info");
		}

		async fetch_fields() {
			this.fields = await this.call("gpf_builder.api.api.get_dunning_letter_fields") || [];
		}

		async fetch_ocr_results() {
			this.ocr_results = await this.call("gpf_builder.api.api.list_ocr_results") || [];
		}

		async fetch_source_values() {
			if (!this.source_docname) {
				this.source_values = {};
				return;
			}
			this.source_values = await this.call("gpf_builder.api.api.get_dunning_letter_doc_values", {
				docname: this.source_docname
			}) || {};
		}

		init_stage() {
			this.stage = new Konva.Stage({
				container: "gpf-canvas-container",
				width: this.page_width,
				height: this.page_height
			});

			this.bg_layer = new Konva.Layer();
			this.layer = new Konva.Layer();
			this.stage.add(this.bg_layer);
			this.stage.add(this.layer);

			this.transformer = new Konva.Transformer({
				rotateEnabled: false,
				ignoreStroke: true
			});
			this.layer.add(this.transformer);
		}

		init_events() {
			$("#btn-upload-pdf").on("click", () => this.upload_pdf());
			$("#btn-save").on("click", () => this.save_layout());
			$("#btn-preview").on("click", () => this.show_preview());
			$("#btn-output").on("click", () => this.show_output());
			$("#btn-finalize").on("click", () => this.finalize());
			$("#btn-edit").on("click", () => this.return_to_editing());
			$("#btn-ocr").on("click", () => this.run_ocr());
			$("#btn-delete").on("click", () => this.delete_selected());
			$("#btn-duplicate").on("click", () => this.duplicate_selected());
			$("#btn-reset").on("click", () => this.reset_layout());
			$("[data-add-block]").on("click", (event) => {
				this.add_block($(event.currentTarget).data("add-block"));
			});

			this.stage.on("click tap", (event) => {
				const block = this.get_block_from_target(event.target);
				this.select_node(block);
			});
		}

		init_source_doc_control() {
			const parent = $("#gpf-source-doc-control");
			parent.empty();
			this.source_doc_control = frappe.ui.form.make_control({
				parent: parent.get(0),
				df: {
					fieldtype: "Link",
					fieldname: "source_docname",
					label: this.setup.target_doctype || "Dunning Letter",
					options: this.setup.target_doctype || "Dunning Letter",
					placeholder: "Select Dunning Letter",
					onchange: async () => {
						this.source_docname = this.source_doc_control.get_value() || "";
						await this.fetch_source_values();
						this.layer.find(".gpf-block").forEach((node) => this.update_block_visual(node));
						this.layer.batchDraw();
						frappe.show_alert({
							message: this.source_docname ? "Source document loaded." : "Source document cleared.",
							indicator: this.source_docname ? "green" : "orange"
						});
					}
				},
				render_input: true
			});
		}

		get_block_from_target(target) {
			if (!target || target === this.stage) return null;
			if (target.hasName && target.hasName("gpf-block")) return target;
			const parent = target.getParent && target.getParent();
			return parent && parent.hasName && parent.hasName("gpf-block") ? parent : null;
		}

		refresh_status() {
			if (!this.setup) return;
			$("#gpf-setup-status").text(`Setup: ${this.setup.name} | ${this.setup.status}`);
			$("#gpf-pdf-status").text(this.setup.pdf_file_url ? `PDF: ${this.setup.pdf_file_name || this.setup.pdf_file_url}` : "No PDF reference selected");
		}

		apply_state_locking() {
			const finalized = this.setup && this.setup.status === "Finalized";
			$("#btn-save, [data-add-block], #btn-delete, #btn-duplicate, #btn-reset, #btn-finalize, #btn-ocr, #btn-upload-pdf").toggle(!finalized);
			$("#btn-edit").toggle(finalized);
			this.layer.find(".gpf-block").forEach((node) => node.draggable(!finalized));
			if (finalized) {
				this.transformer.nodes([]);
				frappe.show_alert({ message: "Setup is finalized and locked.", indicator: "orange" });
			}
		}

		upload_pdf() {
			new frappe.ui.FileUploader({
				restrictions: {
					allowed_file_types: [".pdf"]
				},
				upload_notes: "Upload one private, single-page PDF reference.",
				on_success: async (file_doc) => {
					await this.call("gpf_builder.api.api.upload_pdf_reference", { file_name: file_doc.name || file_doc.file_url });
					await this.fetch_setup();
					this.refresh_status();
					await this.render_pdf_background();
					frappe.show_alert({ message: "PDF reference saved.", indicator: "green" });
				}
			});
		}

		render_field_list() {
			const container = $("#gpf-field-list");
			container.empty();
			if (!this.fields.length) {
				container.html('<div class="text-muted">No fields available.</div>');
				return;
			}
			this.fields.forEach((field) => {
				const button = $(`<button class="btn btn-xs btn-default gpf-field-item"></button>`);
				button.text(`${field.label || field.fieldname} (${field.fieldname})`);
				button.attr("title", field.fieldtype || "");
				button.on("click", () => {
					if (!this.selected_node) return;
					this.selected_node.setAttrs({
						block_type: "Dynamic Field",
						fieldname: field.fieldname
					});
					this.update_block_visual(this.selected_node);
					this.render_properties();
				});
				container.append(button);
			});
		}

		render_ocr_results() {
			const container = $("#gpf-ocr-list");
			container.empty();
			if (!this.ocr_results.length) {
				container.html('<div class="text-muted gpf-side-empty">Run OCR to extract text from the PDF.</div>');
				return;
			}

			this.ocr_results.forEach((result) => {
				const text = result.normalized_text || "";
				const item = $(`
					<div class="gpf-ocr-item">
						<div class="gpf-ocr-status ${result.confirmed ? "confirmed" : "unconfirmed"}">
							${result.confirmed ? "Confirmed" : "Needs confirmation"}
						</div>
						<div class="gpf-ocr-text"></div>
						<div class="gpf-ocr-actions">
							<button class="btn btn-xs btn-primary" data-action="use">Use</button>
							<button class="btn btn-xs btn-default" data-action="view">View</button>
							${result.confirmed ? "" : '<button class="btn btn-xs btn-success" data-action="confirm">Confirm</button>'}
						</div>
					</div>
				`);
				item.find(".gpf-ocr-text").text(text || result.name);
				item.find('[data-action="use"]').on("click", () => this.use_ocr_result(result));
				item.find('[data-action="view"]').on("click", () => this.show_ocr_result(result));
				item.find('[data-action="confirm"]').on("click", () => this.confirm_ocr_result(result.name));
				container.append(item);
			});
		}

		use_ocr_result(result) {
			let node = this.selected_node;
			if (!node || node.getAttr("block_type") !== "OCR Text") {
				node = this.add_block("OCR Text", {
					ocr_result: result.name,
					static_text: "",
					width: 55,
					height: 8
				});
			} else {
				node.setAttrs({
					block_type: "OCR Text",
					ocr_result: result.name
				});
			}
			this.select_node(node);
			this.update_block_visual(node);
			this.render_properties();
			frappe.show_alert({ message: "OCR result applied to block.", indicator: "green" });
		}

		show_ocr_result(result) {
			const dialog = new frappe.ui.Dialog({
				title: result.name,
				size: "large",
				fields: [
					{
						fieldtype: "Text",
						fieldname: "normalized_text",
						label: "Detected Text",
						read_only: 1
					}
				]
			});
			dialog.show();
			dialog.set_value("normalized_text", result.normalized_text || "");
		}

		async confirm_ocr_result(name) {
			await this.call("gpf_builder.api.api.confirm_ocr_result", { ocr_result_name: name });
			await this.fetch_ocr_results();
			this.render_ocr_results();
			frappe.show_alert({ message: "OCR result confirmed.", indicator: "green" });
		}

		async load_blocks() {
			const blocks = await this.call("gpf_builder.api.api.get_layout");
			(blocks || []).forEach((block) => this.add_block(block.block_type, block));
			this.layer.batchDraw();
		}

		add_block(block_type, data) {
			const block = Object.assign({
				block_type,
				x: 8,
				y: 8,
				width: 22,
				height: 5,
				z_index: this.layer.find(".gpf-block").length,
				static_text: block_type === "Static Text" ? "Static text" : "",
				fieldname: "",
				ocr_result: "",
				file_reference: "",
				style_json: "{}"
			}, data || {});

			const group = new Konva.Group({
				x: this.percent_to_x(block.x),
				y: this.percent_to_y(block.y),
				width: this.percent_to_x(block.width),
				height: this.percent_to_y(block.height),
				draggable: !(this.setup && this.setup.status === "Finalized"),
				name: "gpf-block"
			});
			group.setAttrs(block);

			group.add(new Konva.Rect({
				name: "gpf-block-box",
				width: group.width(),
				height: group.height(),
				fill: "rgba(37, 99, 235, 0.08)",
				stroke: "#2563eb",
				strokeWidth: 1
			}));
			group.add(new Konva.Text({
				name: "gpf-block-label",
				x: 0,
				y: 0,
				width: Math.max(group.width(), 20),
				height: Math.max(group.height(), 12),
				fontSize: 12,
				fill: "#1f2937"
			}));

			group.on("transformend", () => {
				this.normalize_block_transform(group);
				this.render_properties();
			});
			group.on("dragend", () => this.render_properties());

			this.layer.add(group);
			this.update_block_visual(group);
			this.select_node(group);
			return group;
		}

		normalize_block_transform(node) {
			const width = Math.max(12, node.width() * node.scaleX());
			const height = Math.max(12, node.height() * node.scaleY());
			node.width(width);
			node.height(height);
			node.scaleX(1);
			node.scaleY(1);
			this.update_block_visual(node);
		}

		update_block_visual(node) {
			const box = node.findOne(".gpf-block-box");
			const label = node.findOne(".gpf-block-label");
			if (box) {
				box.width(node.width());
				box.height(node.height());
			}
			if (label) {
				const styles = this.get_style_attrs(node);
				const font_weight = styles["font-weight"] || "normal";
				const font_style = styles["font-style"] || "normal";
				const konva_font_style = [
					["bold", "700", "600"].includes(String(font_weight)) ? "bold" : "",
					font_style === "italic" ? "italic" : ""
				].filter(Boolean).join(" ") || "normal";

				label.x(0);
				label.y(0);
				label.width(Math.max(node.width(), 20));
				label.height(Math.max(node.height(), 12));
				label.fontSize(this.css_size_to_number(styles["font-size"], 12));
				label.fontFamily(styles["font-family"] || "Arial");
				label.fontStyle(konva_font_style);
				label.align(styles["text-align"] || "left");
				label.lineHeight(this.css_number(styles["line-height"], 1.2));
				label.fill(styles.color || "#1f2937");
				label.scaleX(1);
				label.scaleY(1);
				label.text(this.get_block_label(node));
			}
			this.layer.batchDraw();
		}

		get_block_label(node) {
			const type = node.getAttr("block_type");
			if (type === "Static Text") return node.getAttr("static_text") || "Static text";
			if (type === "Dynamic Field") {
				const fieldname = node.getAttr("fieldname");
				return this.source_values[fieldname] || fieldname || "Select a field";
			}
			if (type === "OCR Text") return node.getAttr("ocr_result") || "OCR text";
			if (type === "Image" || type === "Branding") return node.getAttr("file_reference") || type;
			return type || "Block";
		}

		select_node(node) {
			this.selected_node = node;
			this.transformer.nodes(node ? [node] : []);
			this.render_properties();
			this.layer.batchDraw();
		}

		render_properties() {
			const container = $("#gpf-properties-content");
			container.empty();
			if (!this.selected_node) {
				container.html('<div class="text-muted text-center gpf-empty-state">Select a block to edit.</div>');
				return;
			}

			const attrs = this.selected_node.attrs;
			const styles = this.get_style_attrs(this.selected_node);
			container.html(`
				<div class="property-group">
					<div class="property-label">Block Type</div>
					<select class="form-control input-sm property-input" data-prop="block_type">
						${["Static Text", "Dynamic Field", "OCR Text", "Image", "Branding"].map((type) =>
							`<option value="${type}" ${attrs.block_type === type ? "selected" : ""}>${type}</option>`
						).join("")}
					</select>
				</div>
				<div class="property-group">
					<div class="property-label">Static Text</div>
					<textarea class="form-control input-sm property-input" data-prop="static_text" rows="3">${this.escape_html(attrs.static_text || "")}</textarea>
				</div>
				<div class="property-group">
					<div class="property-label">Fieldname</div>
					<input class="form-control input-sm property-input" data-prop="fieldname" value="${this.escape_html(attrs.fieldname || "")}">
				</div>
				<div class="property-group">
					<div class="property-label">OCR Result</div>
					<input class="form-control input-sm property-input" data-prop="ocr_result" value="${this.escape_html(attrs.ocr_result || "")}">
				</div>
				<div class="property-group">
					<div class="property-label">File Reference</div>
					<input class="form-control input-sm property-input" data-prop="file_reference" value="${this.escape_html(attrs.file_reference || "")}">
				</div>
				<div class="property-group">
					<div class="property-label">Text Appearance</div>
					<div class="row">
						<div class="col-xs-6">
							<div class="property-label">Font Size</div>
							<input type="number" min="1" step="0.5" class="form-control input-sm property-input" data-prop="style_font_size" value="${this.css_size_to_number(styles["font-size"], 12)}">
						</div>
						<div class="col-xs-6">
							<div class="property-label">Line Height</div>
							<input type="number" min="0.5" step="0.05" class="form-control input-sm property-input" data-prop="style_line_height" value="${this.css_number(styles["line-height"], 1.2)}">
						</div>
					</div>
					<div class="row" style="margin-top:8px;">
						<div class="col-xs-6">
							<div class="property-label">Weight</div>
							<select class="form-control input-sm property-input" data-prop="style_font_weight">
								<option value="normal" ${styles["font-weight"] !== "bold" ? "selected" : ""}>Normal</option>
								<option value="bold" ${styles["font-weight"] === "bold" ? "selected" : ""}>Bold</option>
							</select>
						</div>
						<div class="col-xs-6">
							<div class="property-label">Align</div>
							<select class="form-control input-sm property-input" data-prop="style_text_align">
								${["left", "center", "right"].map((align) =>
									`<option value="${align}" ${(styles["text-align"] || "left") === align ? "selected" : ""}>${align}</option>`
								).join("")}
							</select>
						</div>
					</div>
					<div class="row" style="margin-top:8px;">
						<div class="col-xs-6">
							<div class="property-label">Color</div>
							<input type="color" class="form-control input-sm property-input gpf-color-input" data-prop="style_color" value="${this.escape_html(styles.color || "#1f2937")}">
						</div>
						<div class="col-xs-6">
							<div class="property-label">Style</div>
							<select class="form-control input-sm property-input" data-prop="style_font_style">
								<option value="normal" ${styles["font-style"] !== "italic" ? "selected" : ""}>Normal</option>
								<option value="italic" ${styles["font-style"] === "italic" ? "selected" : ""}>Italic</option>
							</select>
						</div>
					</div>
				</div>
				<div class="property-group">
					<div class="row">
						<div class="col-xs-6"><div class="property-label">X %</div><input type="number" class="form-control input-sm property-input" data-prop="x_pct" value="${this.x_to_percent(this.selected_node.x()).toFixed(2)}"></div>
						<div class="col-xs-6"><div class="property-label">Y %</div><input type="number" class="form-control input-sm property-input" data-prop="y_pct" value="${this.y_to_percent(this.selected_node.y()).toFixed(2)}"></div>
					</div>
					<div class="row" style="margin-top:8px;">
						<div class="col-xs-6"><div class="property-label">W %</div><input type="number" class="form-control input-sm property-input" data-prop="width_pct" value="${this.x_to_percent(this.selected_node.width() * this.selected_node.scaleX()).toFixed(2)}"></div>
						<div class="col-xs-6"><div class="property-label">H %</div><input type="number" class="form-control input-sm property-input" data-prop="height_pct" value="${this.y_to_percent(this.selected_node.height() * this.selected_node.scaleY()).toFixed(2)}"></div>
					</div>
				</div>
			`);

			container.find(".property-input").on("change keyup", (event) => {
				this.update_selected_property($(event.currentTarget).data("prop"), $(event.currentTarget).val());
			});
		}

		update_selected_property(prop, value) {
			if (!this.selected_node) return;
			if (["x_pct", "y_pct", "width_pct", "height_pct"].includes(prop)) {
				const numeric = this.to_number(value);
				if (prop === "x_pct") this.selected_node.x(this.percent_to_x(numeric));
				if (prop === "y_pct") this.selected_node.y(this.percent_to_y(numeric));
				if (prop === "width_pct") {
					this.selected_node.width(this.percent_to_x(numeric));
					this.selected_node.scaleX(1);
				}
				if (prop === "height_pct") {
					this.selected_node.height(this.percent_to_y(numeric));
					this.selected_node.scaleY(1);
				}
			} else if (prop && prop.indexOf("style_") === 0) {
				this.update_selected_style(prop, value);
			} else {
				this.selected_node.setAttr(prop, value);
			}
			this.update_block_visual(this.selected_node);
		}

		update_selected_style(prop, value) {
			const style_map = {
				style_font_size: "font-size",
				style_font_weight: "font-weight",
				style_text_align: "text-align",
				style_color: "color",
				style_line_height: "line-height",
				style_font_style: "font-style"
			};
			const css_prop = style_map[prop];
			if (!css_prop) return;

			const styles = this.get_style_attrs(this.selected_node);
			if (prop === "style_font_size") {
				const size = this.css_number(value, 12);
				styles[css_prop] = `${size}px`;
			} else if (prop === "style_line_height") {
				styles[css_prop] = this.css_number(value, 1.2);
			} else {
				styles[css_prop] = value;
			}
			this.selected_node.setAttr("style_json", JSON.stringify(styles));
		}

		delete_selected() {
			if (!this.selected_node) return;
			this.selected_node.destroy();
			this.select_node(null);
		}

		duplicate_selected() {
			if (!this.selected_node) return;
			const data = this.serialize_block(this.selected_node);
			data.x = Math.min(data.x + 2, 95);
			data.y = Math.min(data.y + 2, 95);
			this.add_block(data.block_type, data);
		}

		reset_layout() {
			const block_count = this.layer.find(".gpf-block").length;
			if (!block_count) {
				frappe.show_alert({ message: "No blocks to reset.", indicator: "orange" });
				return;
			}

			frappe.confirm("Clear all layout blocks?", async () => {
				this.layer.find(".gpf-block").forEach((node) => node.destroy());
				this.select_node(null);
				this.layer.batchDraw();
				await this.save_layout({ silent: true });
				frappe.show_alert({ message: "Layout reset.", indicator: "green" });
			});
		}

		serialize_block(node, index) {
			this.normalize_block_transform(node);
			const width = node.width() * node.scaleX();
			const height = node.height() * node.scaleY();
			return {
				block_type: node.getAttr("block_type"),
				x: this.x_to_percent(node.x()),
				y: this.y_to_percent(node.y()),
				width: this.x_to_percent(width),
				height: this.y_to_percent(height),
				z_index: index || 0,
				static_text: node.getAttr("static_text") || "",
				fieldname: node.getAttr("fieldname") || "",
				ocr_result: node.getAttr("ocr_result") || "",
				file_reference: node.getAttr("file_reference") || "",
				style_json: node.getAttr("style_json") || "{}"
			};
		}

		async save_layout(options) {
			const blocks = this.layer.find(".gpf-block").map((node, index) => this.serialize_block(node, index));
			await this.call("gpf_builder.api.api.save_layout", { blocks_json: JSON.stringify(blocks) });
			if (!(options && options.silent)) {
				frappe.show_alert({ message: "Layout saved.", indicator: "green" });
			}
		}

		async show_preview() {
			const html = await this.call("gpf_builder.api.api.get_preview", {
				docname: this.source_docname || null
			});
			const dialog = new frappe.ui.Dialog({ title: "Layout Preview", size: "extra-large" });
			$(dialog.body).html(`<div style="background:#f3f4f6;padding:16px;">${html || ""}</div>`);
			dialog.show();
		}

		async show_output() {
			const output = await this.call("gpf_builder.api.api.generate_output", {
				docname: this.source_docname || null
			});
			const dialog = new frappe.ui.Dialog({
				title: "Copy-ready Print Format HTML",
				size: "extra-large",
				fields: [{ fieldtype: "Code", fieldname: "html", options: "HTML", label: "HTML", read_only: 1 }]
			});
			dialog.show();
			dialog.set_value("html", output || "");
		}

		async finalize() {
			frappe.confirm("Finalize and lock this layout?", async () => {
				await this.save_layout();
				await this.call("gpf_builder.api.api.finalize_setup");
				await this.fetch_setup();
				this.refresh_status();
				this.apply_state_locking();
			});
		}

		async return_to_editing() {
			await this.call("gpf_builder.api.api.return_to_editing");
			await this.fetch_setup();
			this.refresh_status();
			this.apply_state_locking();
		}

		async run_ocr() {
			if (!this.setup || !this.setup.pdf_reference_file) {
				frappe.msgprint("Upload and save a PDF reference first.");
				return;
			}
			if (!this.selected_node || this.selected_node.getAttr("block_type") !== "OCR Text") {
				frappe.msgprint("Select or create an OCR Text block, place it over the PDF text, then run OCR.");
				return;
			}

			const region = this.serialize_block(this.selected_node);
			const result = await this.call("gpf_builder.api.api.run_ocr", {
				file_name: this.setup.pdf_reference_file,
				region_json: JSON.stringify({
					x: region.x,
					y: region.y,
					width: region.width,
					height: region.height
				})
			});
			await this.fetch_ocr_results();
			this.render_ocr_results();
			const created = this.ocr_results.find((item) => item.name === result.ocr_result);
			if (created) {
				this.selected_node.setAttr("ocr_result", created.name);
				this.update_block_visual(this.selected_node);
				this.render_properties();
				this.show_ocr_result(created);
			}
			frappe.show_alert({ message: "OCR scanned the selected block.", indicator: "green" });
		}

		async render_pdf_background() {
			if (!this.setup || !this.setup.pdf_file_url) return;
			try {
				const pdf = await pdfjsLib.getDocument(frappe.urllib.get_full_url(this.setup.pdf_file_url)).promise;
				const first_page = await pdf.getPage(1);
				const viewport = first_page.getViewport({ scale: 2 });
				const canvas = document.createElement("canvas");
				canvas.width = viewport.width;
				canvas.height = viewport.height;
				await first_page.render({ canvasContext: canvas.getContext("2d"), viewport }).promise;

				const image = new Image();
				image.onload = () => {
					this.bg_layer.destroyChildren();
					this.bg_layer.add(new Konva.Image({
						image,
						x: 0,
						y: 0,
						width: this.page_width,
						height: this.page_height
					}));
					this.bg_layer.draw();
				};
				image.src = canvas.toDataURL();
			} catch (error) {
				console.error(error);
				frappe.show_alert({ message: "Could not render PDF background.", indicator: "red" });
			}
		}

		get_style_attrs(node) {
			try {
				const styles = JSON.parse(node.getAttr("style_json") || "{}");
				return styles && typeof styles === "object" && !Array.isArray(styles) ? styles : {};
			} catch (error) {
				return {};
			}
		}

		css_size_to_number(value, fallback) {
			if (value === undefined || value === null || value === "") return fallback;
			const parsed = parseFloat(String(value).replace("px", ""));
			return Number.isFinite(parsed) ? parsed : fallback;
		}

		css_number(value, fallback) {
			const parsed = parseFloat(value);
			return Number.isFinite(parsed) ? parsed : fallback;
		}

		percent_to_x(value) {
			return this.to_number(value) / 100 * this.page_width;
		}

		percent_to_y(value) {
			return this.to_number(value) / 100 * this.page_height;
		}

		x_to_percent(value) {
			return this.to_number(value) / this.page_width * 100;
		}

		y_to_percent(value) {
			return this.to_number(value) / this.page_height * 100;
		}

		to_number(value) {
			const parsed = parseFloat(value);
			return Number.isFinite(parsed) ? parsed : 0;
		}

		escape_html(value) {
			return String(value || "")
				.replace(/&/g, "&amp;")
				.replace(/</g, "&lt;")
				.replace(/>/g, "&gt;")
				.replace(/"/g, "&quot;")
				.replace(/'/g, "&#039;");
		}
	}
};
