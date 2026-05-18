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
			this.$wrapper = $(".gpf-builder-wrapper").last();
			this.setup = null;
			this.fields = [];
			this.ocr_results = [];
			this.source_docname = "";
			this.source_values = {};
			this.target_doctype_control = null;
			this.source_doc_control = null;
			this.pdf_text = "";
			this.auto_save_timer = null;
			this.is_loading_blocks = false;
			this.stage = null;
			this.bg_layer = null;
			this.layer = null;
			this.guide_layer = null;
			this.transformer = null;
			this.selected_node = null;
			this.image_preview_cache = {};
			this.html_preview_cache = {};
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
			this.init_collapsible_panel();
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
			this.fields = await this.call("gpf_builder.api.api.get_target_fields") || [];
		}

		async fetch_ocr_results() {
			this.ocr_results = await this.call("gpf_builder.api.api.list_ocr_results") || [];
		}

		async fetch_source_values() {
			if (!this.source_docname) {
				this.source_values = {};
				return;
			}
			this.source_values = await this.call("gpf_builder.api.api.get_target_doc_values", {
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
				this.guide_layer = new Konva.Layer();
				this.stage.add(this.bg_layer);
				this.stage.add(this.layer);
				this.stage.add(this.guide_layer);

			this.transformer = new Konva.Transformer({
				rotateEnabled: false,
				ignoreStroke: true
			});
			this.layer.add(this.transformer);
		}

		init_events() {
			this.$wrapper.find("#btn-upload-pdf").off("click.gpf").on("click.gpf", () => this.upload_pdf());
			this.$wrapper.find("#btn-pdf-text").off("click.gpf").on("click.gpf", () => this.show_pdf_text());
			this.$wrapper.find("#btn-save").off("click.gpf").on("click.gpf", () => this.save_layout());
			this.$wrapper.find("#btn-preview").off("click.gpf").on("click.gpf", () => this.show_preview());
			this.$wrapper.find("#btn-output").off("click.gpf").on("click.gpf", () => this.show_output());
			this.$wrapper.find("#btn-finalize").off("click.gpf").on("click.gpf", () => this.finalize());
			this.$wrapper.find("#btn-edit").off("click.gpf").on("click.gpf", () => this.return_to_editing());
			this.$wrapper.find("#btn-ocr").off("click.gpf").on("click.gpf", () => this.run_ocr());
			this.$wrapper.find("#btn-delete").off("click.gpf").on("click.gpf", () => this.delete_selected());
			this.$wrapper.find("#btn-duplicate").off("click.gpf").on("click.gpf", () => this.duplicate_selected());
			this.$wrapper.find("#btn-reset").off("click.gpf").on("click.gpf", () => this.reset_layout());
			this.$wrapper.find("#btn-fullscreen").off("click.gpf").on("click.gpf", () => this.toggle_fullscreen());
			this.$wrapper.find("#btn-v-ruler").off("click.gpf").on("click.gpf", () => this.add_vertical_ruler());
			this.$wrapper.find("#btn-h-ruler").off("click.gpf").on("click.gpf", () => this.add_horizontal_ruler());
			this.$wrapper.find("#btn-clear-rulers").off("click.gpf").on("click.gpf", () => this.clear_rulers());
			this.$wrapper.find("[data-add-block]").off("click.gpf").on("click.gpf", (event) => {
				this.add_block($(event.currentTarget).data("add-block"));
			});

			$(document).off("fullscreenchange.gpf").on("fullscreenchange.gpf", () => this.sync_fullscreen_state());

			this.stage.on("click tap", (event) => {
				const block = this.get_block_from_target(event.target);
				this.select_node(block);
			});
		}

		add_vertical_ruler(percent) {
			const x = this.percent_to_x(percent === undefined ? 50 : percent);
			const group = new Konva.Group({
				x,
				y: 0,
				draggable: true,
				name: "gpf-ruler gpf-v-ruler",
				dragBoundFunc: (pos) => ({
					x: Math.max(0, Math.min(this.page_width, pos.x)),
					y: 0
				})
			});
			group.add(new Konva.Line({
				points: [0, 0, 0, this.page_height],
				stroke: "#ef4444",
				strokeWidth: 1,
				hitStrokeWidth: 18,
				dash: [6, 4]
			}));
			group.add(new Konva.Text({
				name: "gpf-ruler-label",
				x: 4,
				y: 4,
				fontSize: 11,
				fill: "#991b1b",
				padding: 3,
				background: "#fff"
			}));
			this.bind_ruler_cursor(group);
			group.on("dragmove", () => this.update_ruler_label(group));
			group.on("dragend", () => this.update_ruler_label(group));
			this.guide_layer.add(group);
			this.update_ruler_label(group);
			this.guide_layer.draw();
		}

		add_horizontal_ruler(percent) {
			const y = this.percent_to_y(percent === undefined ? 50 : percent);
			const group = new Konva.Group({
				x: 0,
				y,
				draggable: true,
				name: "gpf-ruler gpf-h-ruler",
				dragBoundFunc: (pos) => ({
					x: 0,
					y: Math.max(0, Math.min(this.page_height, pos.y))
				})
			});
			group.add(new Konva.Line({
				points: [0, 0, this.page_width, 0],
				stroke: "#ef4444",
				strokeWidth: 1,
				hitStrokeWidth: 18,
				dash: [6, 4]
			}));
			group.add(new Konva.Text({
				name: "gpf-ruler-label",
				x: 4,
				y: 4,
				fontSize: 11,
				fill: "#991b1b",
				padding: 3,
				background: "#fff"
			}));
			this.bind_ruler_cursor(group);
			group.on("dragmove", () => this.update_ruler_label(group));
			group.on("dragend", () => this.update_ruler_label(group));
			this.guide_layer.add(group);
			this.update_ruler_label(group);
			this.guide_layer.draw();
		}

		bind_ruler_cursor(group) {
			group.on("mouseenter", () => {
				this.stage.container().style.cursor = group.hasName("gpf-v-ruler") ? "ew-resize" : "ns-resize";
			});
			group.on("mouseleave", () => {
				this.stage.container().style.cursor = "default";
			});
			group.on("dragstart", () => {
				this.stage.container().style.cursor = "move";
			});
			group.on("dragend", () => {
				this.stage.container().style.cursor = "default";
			});
		}

		update_ruler_label(group) {
			const label = group.findOne(".gpf-ruler-label");
			if (!label) return;
			if (group.hasName("gpf-v-ruler")) {
				const left = this.x_to_percent(group.x());
				label.text(`L ${left.toFixed(1)}% / R ${(100 - left).toFixed(1)}%`);
			} else {
				const top = this.y_to_percent(group.y());
				label.text(`T ${top.toFixed(1)}% / B ${(100 - top).toFixed(1)}%`);
			}
		}

		clear_rulers() {
			this.guide_layer.destroyChildren();
			this.guide_layer.draw();
		}

		init_collapsible_panel() {
			this.$wrapper.find(".panel-header[data-collapse-target]")
				.off("click.gpf")
				.on("click.gpf", (event) => {
					const header = $(event.currentTarget);
					const target = this.$wrapper.find(header.data("collapse-target"));
					const collapsed = header.toggleClass("is-collapsed").hasClass("is-collapsed");
					target.toggleClass("gpf-panel-collapsed", collapsed);
					header.find("i").toggleClass("fa-chevron-up", !collapsed).toggleClass("fa-chevron-down", collapsed);
				});
		}

		toggle_fullscreen() {
			const wrapper = $(".gpf-builder-wrapper").get(0);
			const is_fullscreen = $(".gpf-builder-wrapper").hasClass("gpf-fullscreen");
			if (is_fullscreen) {
				this.exit_fullscreen();
				return;
			}

			$(".gpf-builder-wrapper").addClass("gpf-fullscreen");
			$("body").addClass("gpf-fullscreen-active");
			$("#btn-fullscreen").html('<i class="fa fa-compress"></i> Exit Fullscreen');
			if (wrapper && wrapper.requestFullscreen) {
				wrapper.requestFullscreen().catch(() => {});
			}
		}

		exit_fullscreen() {
			$(".gpf-builder-wrapper").find(".gpf-preview-overlay").remove();
			$(".gpf-builder-wrapper").removeClass("gpf-fullscreen");
			$("body").removeClass("gpf-fullscreen-active");
			$("#btn-fullscreen").html('<i class="fa fa-expand"></i> Fullscreen');
			if (document.fullscreenElement && document.exitFullscreen) {
				document.exitFullscreen().catch(() => {});
			}
		}

		sync_fullscreen_state() {
			if (!document.fullscreenElement) {
				$(".gpf-builder-wrapper").find(".gpf-preview-overlay").remove();
				$(".gpf-builder-wrapper").removeClass("gpf-fullscreen");
				$("body").removeClass("gpf-fullscreen-active");
				$("#btn-fullscreen").html('<i class="fa fa-expand"></i> Fullscreen');
			}
		}

		init_source_doc_control() {
			const target_parent = $("#gpf-target-doctype-control");
			const source_parent = $("#gpf-source-doc-control");
			const target_doctype = this.get_target_doctype();
			target_parent.empty();
			source_parent.empty();
			this.$wrapper.find(".gpf-source-doc-help").text(`Select a ${target_doctype} document to preview real field values.`);
			this.target_doctype_control = frappe.ui.form.make_control({
				parent: target_parent.get(0),
				df: {
					fieldtype: "Link",
					fieldname: "target_doctype",
					label: "Target DocType",
					options: "DocType",
					placeholder: "Select DocType",
					onchange: async () => {
						const new_doctype = this.target_doctype_control.get_value();
						if (!new_doctype || new_doctype === this.get_target_doctype()) return;
						await this.change_target_doctype(new_doctype);
					}
				},
				render_input: true
			});
			this.target_doctype_control.set_value(target_doctype);

			this.source_doc_control = frappe.ui.form.make_control({
				parent: source_parent.get(0),
				df: {
					fieldtype: "Link",
					fieldname: "source_docname",
					label: target_doctype,
					options: target_doctype,
					placeholder: `Select ${target_doctype}`,
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

		async change_target_doctype(target_doctype) {
			await this.call("gpf_builder.api.api.set_target_doctype", { target_doctype });
			await this.fetch_setup();
			await this.fetch_fields();
			this.source_docname = "";
			this.source_values = {};
			this.ocr_results = [];
			this.pdf_text = "";
			this.layer.destroyChildren();
			this.transformer = new Konva.Transformer({
				rotateEnabled: false,
				ignoreStroke: true
			});
			this.layer.add(this.transformer);
			this.bg_layer.destroyChildren();
			this.clear_rulers();
			this.init_source_doc_control();
			this.render_field_list();
			this.render_ocr_results();
			this.render_properties();
			this.refresh_status();
			this.bg_layer.batchDraw();
			this.layer.batchDraw();
			frappe.show_alert({ message: "Target DocType changed. Builder state was cleared.", indicator: "green" });
		}

		get_target_doctype() {
			return (this.setup && this.setup.target_doctype) || "Source Document";
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
					this.pdf_text = "";
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
					this.schedule_auto_save();
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
			this.schedule_auto_save();
			frappe.show_alert({ message: "OCR result applied to block.", indicator: "green" });
		}

		show_ocr_result(result) {
			if (this.$wrapper.hasClass("gpf-fullscreen")) {
				this.show_fullscreen_text_overlay(result.name, result.normalized_text || "", {
					label: "Detected Text"
				});
				return;
			}
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
			this.is_loading_blocks = true;
			(blocks || []).forEach((block) => this.add_block(block.block_type, block));
			this.is_loading_blocks = false;
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
			group.setAttrs({
				block_type: block.block_type,
				z_index: block.z_index,
				static_text: block.static_text,
				fieldname: block.fieldname,
				ocr_result: block.ocr_result,
				file_reference: block.file_reference,
				style_json: block.style_json
			});

			group.add(new Konva.Rect({
				name: "gpf-block-box",
				width: group.width(),
				height: group.height(),
				fill: "rgba(37, 99, 235, 0.08)",
				stroke: "#2563eb",
				strokeWidth: 1
			}));
			group.add(new Konva.Image({
				name: "gpf-block-image",
				x: 0,
				y: 0,
				width: group.width(),
				height: group.height(),
				visible: false,
				listening: false
			}));
			group.add(new Konva.Image({
				name: "gpf-block-html",
				x: 0,
				y: 0,
				width: group.width(),
				height: group.height(),
				visible: false,
				listening: false
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
				this.schedule_auto_save();
			});
			group.on("dragend", () => {
				this.render_properties();
				this.schedule_auto_save();
			});

			this.layer.add(group);
			this.update_block_visual(group);
			this.select_node(group);
			if (!this.is_loading_blocks) {
				this.schedule_auto_save();
			}
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
			const image = node.findOne(".gpf-block-image");
			const html_image = node.findOne(".gpf-block-html");
			const label = node.findOne(".gpf-block-label");
			const type = node.getAttr("block_type");
			const is_media = type === "Image" || type === "Branding";
			const styles = this.get_style_attrs(node);
			const is_static_text = type === "Static Text";
			if (box) {
				box.width(node.width());
				box.height(node.height());
				box.stroke(node.getAttr("has_overlap") ? "#dc2626" : "#2563eb");
				box.strokeWidth(node.getAttr("has_overlap") ? 2 : 1);
			}
			if (image) {
				image.width(node.width());
				image.height(node.height());
				image.visible(false);
			}
			if (html_image) {
				html_image.width(node.width());
				html_image.height(node.height());
				html_image.visible(false);
			}
			if (label) {
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
				label.visible(true);
			}
			if (is_media) {
				this.sync_block_image_preview(node);
			} else if (is_static_text) {
				this.sync_block_html_preview(node);
			}
			this.layer.batchDraw();
		}

		get_file_reference_url(file_reference) {
			if (!file_reference) return "";
			if (file_reference.startsWith("http://") || file_reference.startsWith("https://")) return file_reference;
			if (file_reference.startsWith("/")) return file_reference;
			return `/files/${encodeURIComponent(file_reference)}`;
		}

		sync_block_image_preview(node) {
			const image_node = node.findOne(".gpf-block-image");
			const label = node.findOne(".gpf-block-label");
			if (!image_node || !label) return;

			const src = this.get_file_reference_url(node.getAttr("file_reference") || "");
			if (!src) {
				image_node.visible(false);
				label.visible(true);
				return;
			}

			const apply_loaded_image = (img) => {
				image_node.image(img);
				image_node.visible(true);
				label.visible(false);
				this.layer.batchDraw();
			};

			const cached = this.image_preview_cache[src];
			if (cached && cached.loaded && cached.image) {
				apply_loaded_image(cached.image);
				return;
			}

			if (!cached) {
				const image = new Image();
				this.image_preview_cache[src] = { loaded: false, image: null };
				image.onload = () => {
					this.image_preview_cache[src] = { loaded: true, image };
					apply_loaded_image(image);
				};
				image.onerror = () => {
					this.image_preview_cache[src] = { loaded: true, image: null };
					image_node.visible(false);
					label.visible(true);
					this.layer.batchDraw();
				};
				image.src = src;
			}
		}

		sync_block_html_preview(node) {
			const html_node = node.findOne(".gpf-block-html");
			const label = node.findOne(".gpf-block-label");
			if (!html_node || !label) return;

			const width = Math.max(1, Math.round(node.width()));
			const height = Math.max(1, Math.round(node.height()));
			const safe_html = this.render_static_html_for_builder(node.getAttr("static_text"));
			const styles = this.get_style_attrs(node);
			const font_size = this.css_size_to_number(styles["font-size"], 12);
			const line_height = this.css_number(styles["line-height"], 1.2);
			const font_family = styles["font-family"] || "Arial";
			const color = styles.color || "#1f2937";
			const text_align = styles["text-align"] || "left";
			const text_align_last = text_align === "justify" ? "auto" : (styles["text-align-last"] || "auto");
			const font_weight = styles["font-weight"] || "normal";
			const font_style = styles["font-style"] || "normal";
			const cache_key = JSON.stringify({
				html: safe_html,
				width,
				height,
				font_size,
				line_height,
				font_family,
				color,
				text_align,
				text_align_last,
				font_weight,
				font_style
			});

			const apply_loaded_image = (img) => {
				html_node.image(img);
				html_node.visible(true);
				label.visible(false);
				this.layer.batchDraw();
			};

			const cached = this.html_preview_cache[cache_key];
			if (cached && cached.loaded && cached.image) {
				apply_loaded_image(cached.image);
				return;
			}

			const image = new Image();
			this.html_preview_cache[cache_key] = { loaded: false, image: null };
			image.onload = () => {
				this.html_preview_cache[cache_key] = { loaded: true, image };
				apply_loaded_image(image);
			};
			image.onerror = () => {
				this.html_preview_cache[cache_key] = { loaded: true, image: null };
				html_node.visible(false);
				label.visible(true);
				this.layer.batchDraw();
			};
			image.src = this.build_html_preview_svg_url({
				html: safe_html,
				width,
				height,
				font_size,
				line_height,
				font_family,
				color,
				text_align,
				text_align_last,
				font_weight,
				font_style
			});
		}

		build_html_preview_svg_url(options) {
			const body_style = [
				`font-size:${options.font_size}px`,
				`line-height:${options.line_height}`,
				`font-family:${this.escape_html(options.font_family)}`,
				`color:${this.escape_html(options.color)}`,
				`text-align:${this.escape_html(options.text_align)}`,
				`text-align-last:${this.escape_html(options.text_align_last)}`,
				`font-weight:${this.escape_html(options.font_weight)}`,
				`font-style:${this.escape_html(options.font_style)}`,
				"margin:0",
				"padding:0",
				"box-sizing:border-box",
				"overflow:hidden",
				"width:100%",
				"height:100%"
			].join(";");
			const span_style = [
				"display:block",
				"width:100%",
				"margin:0",
				"padding:0",
				"white-space:pre-wrap",
				"overflow-wrap:break-word",
				"text-align:inherit",
				"text-align-last:inherit"
			].join(";");
			const svg = `
				<svg xmlns="http://www.w3.org/2000/svg" width="${options.width}" height="${options.height}">
					<foreignObject width="100%" height="100%">
						<div xmlns="http://www.w3.org/1999/xhtml" style="${body_style}">
							<style>span.gpf-builder-plain-text{${span_style}}</style>
							${options.html}
						</div>
					</foreignObject>
				</svg>
			`;
			return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
		}

		get_block_label(node) {
			const type = node.getAttr("block_type");
			if (type === "Static Text") return this.html_to_plain_text(node.getAttr("static_text")) || "Static HTML";
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
					<div class="property-label">HTML</div>
					<textarea class="form-control input-sm property-input" data-prop="static_text" rows="6">${this.escape_html(attrs.static_text || "")}</textarea>
				</div>
				<div class="property-group">
					<div class="property-label">Text Alignment</div>
					<select class="form-control input-sm property-input" data-prop="style_text_align">
						${["left", "center", "right", "justify"].map((align) =>
							`<option value="${align}" ${(styles["text-align"] || "left") === align ? "selected" : ""}>${align}</option>`
						).join("")}
					</select>
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
								${["left", "center", "right", "justify"].map((align) =>
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
			this.schedule_auto_save();
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
			} else if (prop === "style_text_align") {
				styles[css_prop] = value;
				delete styles["text-align-last"];
			} else {
				styles[css_prop] = value;
			}
			this.selected_node.setAttr("style_json", JSON.stringify(styles));
		}

		delete_selected() {
			if (!this.selected_node) return;
			this.selected_node.destroy();
			this.select_node(null);
			this.schedule_auto_save();
		}

		duplicate_selected() {
			if (!this.selected_node) {
				frappe.show_alert({ message: "Select a block to duplicate.", indicator: "orange" });
				return;
			}
			const data = this.serialize_block(this.selected_node);
			const offset = 2;
			data.x = Math.min(data.x + offset, Math.max(0, 100 - data.width));
			data.y = Math.min(data.y + offset, Math.max(0, 100 - data.height));
			data.z_index = this.layer.find(".gpf-block").length;
			const duplicated = this.add_block(data.block_type, data);
			this.select_node(duplicated);
			this.render_properties();
			frappe.show_alert({ message: "Block duplicated.", indicator: "green" });
		}

		reset_layout() {
			frappe.confirm("Reset the builder? This clears the PDF reference, layout blocks, OCR results, and source document selection.", async () => {
				await this.call("gpf_builder.api.api.reset_setup");
				this.selected_node = null;
				this.transformer.nodes([]);
				this.layer.destroyChildren();
				this.transformer = new Konva.Transformer({
					rotateEnabled: false,
					ignoreStroke: true
				});
				this.layer.add(this.transformer);
				this.bg_layer.destroyChildren();
				this.clear_rulers();
				this.ocr_results = [];
				this.source_docname = "";
				this.source_values = {};
				this.pdf_text = "";
				if (this.source_doc_control) {
					this.source_doc_control.set_value("");
				}
				await this.fetch_setup();
				this.render_properties();
				this.render_ocr_results();
				this.refresh_status();
				this.apply_state_locking();
				this.bg_layer.batchDraw();
				this.layer.batchDraw();
				frappe.show_alert({ message: "Builder reset.", indicator: "green" });
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
			this.clear_overlap_highlights();
			const blocks = this.layer.find(".gpf-block").map((node, index) => this.serialize_block(node, index));
			await this.call("gpf_builder.api.api.save_layout", { blocks_json: JSON.stringify(blocks) });
			if (!(options && options.silent)) {
				frappe.show_alert({ message: "Layout saved.", indicator: "green" });
			}
		}

		schedule_auto_save() {
			if (this.is_loading_blocks || (this.setup && this.setup.status === "Finalized")) {
				return;
			}
			if (!this.can_auto_save_layout()) {
				return;
			}

			clearTimeout(this.auto_save_timer);
				this.auto_save_timer = setTimeout(async () => {
					try {
						await this.save_layout({ silent: true });
					} catch (error) {
						console.error(error);
						frappe.show_alert({ message: "Auto-save failed.", indicator: "red" });
					}
			}, 700);
		}

		can_auto_save_layout() {
			return !this.layer.find(".gpf-block").some((node) => {
				return node.getAttr("block_type") === "Dynamic Field" && !node.getAttr("fieldname");
			});
		}

		async show_preview() {
			const html = await this.call("gpf_builder.api.api.get_preview", {
				docname: this.source_docname || null
			});
			if (this.$wrapper.hasClass("gpf-fullscreen")) {
				this.show_fullscreen_preview(html || "");
				return;
			}
			const dialog = new frappe.ui.Dialog({ title: "Layout Preview", size: "extra-large" });
			$(dialog.body).html(`<div class="gpf-preview-dialog-page">${html || ""}</div>`);
			dialog.show();
		}

		show_fullscreen_preview(html) {
			this.$wrapper.find(".gpf-preview-overlay").remove();
			const overlay = $(`
				<div class="gpf-preview-overlay">
					<div class="gpf-preview-overlay-header">
						<div class="gpf-preview-overlay-title">Layout Preview</div>
						<button class="btn btn-default btn-sm" type="button" data-action="close-preview">
							<i class="fa fa-times"></i> Close
						</button>
					</div>
					<div class="gpf-preview-overlay-body">
						<div class="gpf-preview-dialog-page">${html}</div>
					</div>
				</div>
			`);
			overlay.find('[data-action="close-preview"]').on("click", () => overlay.remove());
			overlay.on("click", (event) => {
				if (event.target === overlay.get(0)) {
					overlay.remove();
				}
			});
			this.$wrapper.append(overlay);
		}

		show_fullscreen_text_overlay(title, text, options) {
			this.$wrapper.find(".gpf-preview-overlay").remove();
			const opts = options || {};
			const overlay = $(`
				<div class="gpf-preview-overlay">
					<div class="gpf-preview-overlay-header">
						<div>
							<div class="gpf-preview-overlay-title"></div>
							<div class="gpf-preview-overlay-subtitle"></div>
						</div>
						<div class="gpf-preview-overlay-actions">
							${opts.copy ? '<button class="btn btn-primary btn-sm" type="button" data-action="copy-text"><i class="fa fa-copy"></i> Copy</button>' : ""}
							<button class="btn btn-default btn-sm" type="button" data-action="close-preview">
								<i class="fa fa-times"></i> Close
							</button>
						</div>
					</div>
					<div class="gpf-preview-overlay-body">
						<div class="gpf-fullscreen-text-card">
							<textarea class="form-control gpf-fullscreen-textarea" readonly></textarea>
						</div>
					</div>
				</div>
			`);
			overlay.find(".gpf-preview-overlay-title").text(title || "Text");
			overlay.find(".gpf-preview-overlay-subtitle").text(opts.label || "");
			overlay.find(".gpf-fullscreen-textarea").val(text || "");
			overlay.find('[data-action="close-preview"]').on("click", () => overlay.remove());
			overlay.find('[data-action="copy-text"]').on("click", () => {
				navigator.clipboard.writeText(text || "");
				frappe.show_alert({ message: "Text copied.", indicator: "green" });
			});
			overlay.on("click", (event) => {
				if (event.target === overlay.get(0)) {
					overlay.remove();
				}
			});
			this.$wrapper.append(overlay);
		}

		copy_to_clipboard(text, success_message) {
			const value = text || "";
			if (navigator.clipboard && window.isSecureContext) {
				return navigator.clipboard.writeText(value).then(() => {
					frappe.show_alert({ message: success_message || "Copied.", indicator: "green" });
				});
			}

			const textarea = document.createElement("textarea");
			textarea.value = value;
			textarea.setAttribute("readonly", "");
			textarea.style.position = "fixed";
			textarea.style.left = "-9999px";
			document.body.appendChild(textarea);
			textarea.select();
			document.execCommand("copy");
			document.body.removeChild(textarea);
			frappe.show_alert({ message: success_message || "Copied.", indicator: "green" });
			return Promise.resolve();
		}

		async show_output() {
			const output = await this.call("gpf_builder.api.api.generate_output", {
				docname: this.source_docname || null
			});
			const dialog = new frappe.ui.Dialog({
				title: "Copy-ready Print Format HTML",
				size: "extra-large",
				fields: [{ fieldtype: "Code", fieldname: "html", options: "HTML", label: "HTML", read_only: 1 }],
				primary_action_label: "Copy HTML",
				primary_action: () => {
					this.copy_to_clipboard(output || "", "Print Format HTML copied.");
				}
			});
			dialog.show();
			dialog.set_value("html", output || "");
			dialog.get_primary_btn().removeClass("btn-primary").addClass("btn-success");
		}

		async finalize() {
			const overlap = this.find_first_overlap();
			if (overlap) {
				this.highlight_overlap(overlap);
				frappe.msgprint({
					title: "Overlapping Blocks",
					indicator: "red",
					message: `These blocks overlap: <b>${this.escape_html(this.get_block_label(overlap[0]))}</b> and <b>${this.escape_html(this.get_block_label(overlap[1]))}</b>.<br>Move or resize one before finalizing.`
				});
				return;
			}

			frappe.confirm("Finalize and lock this layout?", async () => {
				await this.save_layout();
				await this.call("gpf_builder.api.api.finalize_setup");
				await this.fetch_setup();
				this.refresh_status();
				this.apply_state_locking();
			});
		}

		find_first_overlap() {
			const blocks = this.layer.find(".gpf-block");
			for (let i = 0; i < blocks.length; i++) {
				for (let j = i + 1; j < blocks.length; j++) {
					if (this.is_media_block(blocks[i]) || this.is_media_block(blocks[j])) {
						continue;
					}
					if (this.blocks_overlap(blocks[i], blocks[j])) {
						return [blocks[i], blocks[j]];
					}
				}
			}
			return null;
		}

		blocks_overlap(a, b) {
			const a_box = this.serialize_block(a);
			const b_box = this.serialize_block(b);
			const intersects = (
				a_box.x < b_box.x + b_box.width &&
				a_box.x + a_box.width > b_box.x &&
				a_box.y < b_box.y + b_box.height &&
				a_box.y + a_box.height > b_box.y
			);
			return intersects && !this.is_allowed_overlap(a, b);
		}

		is_allowed_overlap(a, b) {
			return (
				this.is_punctuation_static_text(a)
				|| this.is_punctuation_static_text(b)
				|| this.is_media_block(a)
				|| this.is_media_block(b)
			);
		}

		is_media_block(node) {
			const type = String(node.getAttr("block_type") || "").toLowerCase();
			return ["image", "branding"].includes(type);
		}

		is_punctuation_static_text(node) {
			if (node.getAttr("block_type") !== "Static Text") return false;
			const text = String(node.getAttr("static_text") || "").trim();
			return !!text && text.length <= 3 && /^[\s:;,.\-\/()[\]{}]+$/.test(text);
		}

		highlight_overlap(nodes) {
			this.clear_overlap_highlights();
			nodes.forEach((node) => {
				node.setAttr("has_overlap", true);
				this.update_block_visual(node);
			});
			this.select_node(nodes[0]);
		}

		clear_overlap_highlights() {
			this.layer.find(".gpf-block").forEach((node) => {
				if (node.getAttr("has_overlap")) {
					node.setAttr("has_overlap", false);
					this.update_block_visual(node);
				}
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

		async show_pdf_text() {
			if (!this.setup || !this.setup.pdf_file_url) {
				frappe.msgprint("Upload a PDF reference first.");
				return;
			}

			if (!this.pdf_text) {
				this.pdf_text = await this.extract_pdf_text();
			}

			if (!this.pdf_text) {
				frappe.confirm("No selectable text was found. Run full-page OCR to extract copyable text?", async () => {
					this.pdf_text = await this.extract_pdf_text_with_ocr();
					this.open_pdf_text_dialog();
				}, () => {
					this.open_pdf_text_dialog();
				});
				return;
			}

			this.open_pdf_text_dialog();
		}

		open_pdf_text_dialog() {
			if (this.$wrapper.hasClass("gpf-fullscreen")) {
				this.show_fullscreen_text_overlay("Selectable PDF Text", this.pdf_text || "No selectable text found in this PDF.", {
					label: "PDF Text",
					copy: true
				});
				return;
			}
			const dialog = new frappe.ui.Dialog({
				title: "Selectable PDF Text",
				size: "large",
				fields: [
					{
						fieldtype: "Text",
						fieldname: "pdf_text",
						label: "PDF Text",
						read_only: 1
					}
				],
				primary_action_label: "Copy",
				primary_action: () => {
					navigator.clipboard.writeText(this.pdf_text || "");
					frappe.show_alert({ message: "PDF text copied.", indicator: "green" });
				}
			});
			dialog.show();
			dialog.set_value("pdf_text", this.pdf_text || "No selectable text found in this PDF.");
		}

		async extract_pdf_text_with_ocr() {
			try {
				const result = await this.call("gpf_builder.api.api.run_ocr", {
					file_name: this.setup.pdf_reference_file
				});
				await this.fetch_ocr_results();
				this.render_ocr_results();
				const created = this.ocr_results.find((item) => item.name === result.ocr_result);
				if (created && created.normalized_text) {
					frappe.show_alert({ message: "Full-page OCR text extracted.", indicator: "green" });
					return created.normalized_text;
				}
			} catch (error) {
				console.error(error);
			}
			frappe.show_alert({ message: "Could not extract text with OCR.", indicator: "red" });
			return "";
		}

		async extract_pdf_text() {
			try {
				const pdf = await pdfjsLib.getDocument(frappe.urllib.get_full_url(this.setup.pdf_file_url)).promise;
				const first_page = await pdf.getPage(1);
				const text_content = await first_page.getTextContent();
				return text_content.items
					.map((item) => item.str || "")
					.filter(Boolean)
					.join(" ")
					.replace(/\s+/g, " ")
					.trim();
			} catch (error) {
				console.error(error);
				frappe.show_alert({ message: "Could not extract PDF text.", indicator: "red" });
				return "";
			}
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

		html_to_plain_text(value) {
			const element = document.createElement("div");
			element.innerHTML = String(value || "");
			return (element.textContent || element.innerText || "").trim();
		}

		has_html_tags(value) {
			return /<\/?[a-z][\s\S]*>/i.test(String(value || ""));
		}

		sanitize_static_html_for_preview(value) {
			const container = document.createElement("div");
			container.innerHTML = String(value || "");
			container.querySelectorAll("script, iframe, object, embed, link, meta").forEach((node) => node.remove());
			container.querySelectorAll("*").forEach((node) => {
				Array.from(node.attributes).forEach((attr) => {
					const name = attr.name.toLowerCase();
					const val = String(attr.value || "").trim().toLowerCase();
					if (name.startsWith("on") || val.startsWith("javascript:")) {
						node.removeAttribute(attr.name);
					}
				});
			});
			const serializer = new XMLSerializer();
			return Array.from(container.childNodes)
				.map((node) => serializer.serializeToString(node))
				.join("");
		}

		render_static_html_for_builder(value) {
			const raw = String(value || "");
			const safe_html = this.sanitize_static_html_for_preview(raw);
			if (this.has_html_tags(safe_html)) {
				return safe_html;
			}
			return `<span class="gpf-builder-plain-text">${this.escape_html(raw)}</span>`;
		}
	}
};
