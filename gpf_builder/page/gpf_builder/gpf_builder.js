frappe.pages['gpf-builder'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'GPF Print Format Builder',
		single_column: true
	});

	// Load HTML and CSS
	$(frappe.render_template("gpf_builder", {})).appendTo(page.main);
	
	// Builder Instance
	class GPFBuilder {
		constructor() {
			this.setup_name = null;
			this.stage = null;
			this.layer = null;
			this.bg_layer = null;
			this.transformer = null;
			this.selected_node = null;
			
			this.init();
		}

		async init() {
			await this.fetch_setup();
			this.init_stage();
			this.init_events();
			this.load_blocks();
			this.render_pdf_background();
			this.apply_state_locking();
		}

		apply_state_locking() {
			if (this.status === 'Finalized') {
				$('#btn-save, #btn-add-text, #btn-add-field, #btn-finalize, #btn-ocr').hide();
				$('#btn-edit').show();
				this.layer.find('.gpf-block').forEach(n => n.draggable(false));
				this.transformer.nodes([]);
				frappe.show_alert({ message: "Setup is Finalized (Locked)", indicator: "orange" });
			}
		}

		async fetch_setup() {
			const r = await frappe.call({
				method: "gpf_builder.gpf_builder.api.api.get_active_setup_info"
			});
			if (r.message) {
				this.setup_name = r.message.name;
				this.pdf_file = r.message.pdf_reference_file;
				this.status = r.message.status;
			}
		}

		init_stage() {
			const width = 800; // Fixed width for builder, height calculated by A4 ratio
			const height = width * 1.414;
			
			this.stage = new Konva.Stage({
				container: 'gpf-canvas-container',
				width: width,
				height: height
			});

			this.bg_layer = new Konva.Layer();
			this.layer = new Konva.Layer();
			
			this.stage.add(this.bg_layer);
			this.stage.add(this.layer);

			this.transformer = new Konva.Transformer();
			this.layer.add(this.transformer);
		}

		init_events() {
			$('#btn-save').click(() => this.save_layout());
			$('#btn-add-text').click(() => this.add_block("Static Text"));
			$('#btn-add-field').click(() => this.add_block("Dynamic Field"));
			$('#btn-preview').click(() => this.show_preview());
			$('#btn-finalize').click(() => this.finalize());
			$('#btn-ocr').click(() => this.run_ocr_global());
			$('#btn-history').click(() => this.show_history());
			$('#btn-edit').click(() => this.return_to_editing());
			
			this.stage.on('click tap', (e) => {
				if (e.target === this.stage) {
					this.select_node(null);
					return;
				}
				this.select_node(e.target);
			});
		}

		async show_history() {
			const r = await frappe.call({
				method: "frappe.client.get_list",
				args: {
					doctype: "GPF Version History",
					filters: { setup: this.setup_name },
					fields: ["version_number", "event_type", "change_summary", "created_at"],
					order_by: "version_number desc"
				}
			});
			if (r.message) {
				const d = new frappe.ui.Dialog({
					title: 'Version History',
					size: 'large'
				});
				let html = '<table class="table table-bordered"><thead><tr><th>Ver</th><th>Event</th><th>Summary</th><th>Date</th></tr></thead><tbody>';
				r.message.forEach(v => {
					html += `<tr><td>${v.version_number}</td><td>${v.event_type}</td><td>${v.change_summary}</td><td>${v.created_at}</td></tr>`;
				});
				html += '</tbody></table>';
				$(d.body).html(html);
				d.show();
			}
		}

		async return_to_editing() {
			frappe.confirm('Return setup to editing state?', async () => {
				await frappe.call({
					method: "gpf_builder.gpf_builder.api.api.return_to_editing"
				});
				frappe.show_alert("Returned to editing.");
				location.reload();
			});
		}

		async show_preview() {
			const r = await frappe.call({
				method: "gpf_builder.gpf_builder.api.api.get_preview"
			});
			if (r.message) {
				const d = new frappe.ui.Dialog({
					title: 'Layout Preview',
					size: 'large'
				});
				$(d.body).html(`<div style="padding:20px; background:#eee;">${r.message}</div>`);
				d.show();
			}
		}

		async finalize() {
			frappe.confirm('Are you sure you want to finalize this layout? This will lock editing.', async () => {
				await frappe.call({
					method: "gpf_builder.gpf_builder.api.api.finalize_setup"
				});
				frappe.show_alert("Setup finalized.");
				location.reload(); // Refresh to apply locked state
			});
		}

		async run_ocr_global() {
			if (!this.pdf_file) return;
			frappe.show_alert("Running OCR...");
			await frappe.call({
				method: "gpf_builder.gpf_builder.api.api.run_ocr",
				args: { file_name: this.pdf_file }
			});
			frappe.show_alert("OCR process completed.");
		}

		add_block(type) {
			const rect = new Konva.Rect({
				x: 50,
				y: 50,
				width: 100,
				height: 30,
				fill: 'rgba(52, 152, 219, 0.2)',
				stroke: '#3498db',
				strokeWidth: 1,
				draggable: true,
				name: 'gpf-block',
				type: type
			});

			this.layer.add(rect);
			this.select_node(rect);
		}

		select_node(node) {
			this.selected_node = node;
			this.transformer.nodes(node ? [node] : []);
			this.render_properties();
		}

		select_node(node) {
			this.selected_node = node;
			this.transformer.nodes(node ? [node] : []);
			this.render_properties();
		}

		render_properties() {
			const container = $('#gpf-properties-content');
			container.empty();
			
			if (!this.selected_node) {
				container.html('<div class="text-muted text-center" style="padding: 20px;">Select a block to edit.</div>');
				return;
			}

			const attrs = this.selected_node.attrs;
			const html = `
				<div class="property-group">
					<div class="property-label">Block Type</div>
					<select class="form-control input-sm property-input" data-prop="type">
						<option value="Static Text" ${attrs.type === 'Static Text' ? 'selected' : ''}>Static Text</option>
						<option value="Dynamic Field" ${attrs.type === 'Dynamic Field' ? 'selected' : ''}>Dynamic Field</option>
						<option value="OCR Text" ${attrs.type === 'OCR Text' ? 'selected' : ''}>OCR Text</option>
						<option value="Branding" ${attrs.type === 'Branding' ? 'selected' : ''}>Branding Asset</option>
					</select>
				</div>
				${this._render_type_specific_fields(attrs)}
				<div class="property-group">
					<div class="row">
						<div class="col-xs-6">
							<div class="property-label">X (%)</div>
							<input type="number" class="form-control input-sm property-input" data-prop="x_pct" value="${Math.round(attrs.x / this.stage.width() * 100)}">
						</div>
						<div class="col-xs-6">
							<div class="property-label">Y (%)</div>
							<input type="number" class="form-control input-sm property-input" data-prop="y_pct" value="${Math.round(attrs.y / this.stage.height() * 100)}">
						</div>
					</div>
				</div>
			`;
			
			container.append(html);
			
			container.find('.property-input').on('change input', (e) => {
				const prop = $(e.target).data('prop');
				const val = $(e.target).val();
				this.update_selected_node(prop, val);
			});
		}

		_render_type_specific_fields(attrs) {
			if (attrs.type === 'Static Text') {
				return `
					<div class="property-group">
						<div class="property-label">Static Content</div>
						<textarea class="form-control input-sm property-input" data-prop="static_text" rows="3">${attrs.static_text || ''}</textarea>
					</div>
				`;
			} else if (attrs.type === 'Dynamic Field') {
				return `
					<div class="property-group">
						<div class="property-label">Field Name</div>
						<input type="text" class="form-control input-sm property-input" data-prop="fieldname" value="${attrs.fieldname || ''}" placeholder="e.g. customer_name">
					</div>
				`;
			} else if (attrs.type === 'OCR Text') {
				return `
					<div class="property-group">
						<div class="property-label">OCR Reference</div>
						<input type="text" class="form-control input-sm property-input" data-prop="ocr_result" value="${attrs.ocr_result || ''}" placeholder="OCR Result ID">
						<button class="btn btn-default btn-xs" style="margin-top:5px;" onclick="gpf_builder_instance.confirm_ocr('${attrs.ocr_result}')">Confirm OCR</button>
					</div>
				`;
			} else if (attrs.type === 'Branding') {
				return `
					<div class="property-group">
						<div class="property-label">Asset File</div>
						<input type="text" class="form-control input-sm property-input" data-prop="file_reference" value="${attrs.file_reference || ''}" placeholder="File Name">
					</div>
				`;
			}
			return '';
		}

		async confirm_ocr(ocr_name) {
			if (!ocr_name) return;
			await frappe.call({
				method: "gpf_builder.gpf_builder.api.api.confirm_ocr_result",
				args: { ocr_result_name: ocr_name }
			});
			frappe.show_alert("OCR Result confirmed.");
		}

		update_selected_node(prop, val) {
			if (!this.selected_node) return;
			
			if (prop === 'type') this.selected_node.setAttr('type', val);
			if (prop === 'static_text') this.selected_node.setAttr('static_text', val);
			if (prop === 'fieldname') this.selected_node.setAttr('fieldname', val);
			if (prop === 'ocr_result') this.selected_node.setAttr('ocr_result', val);
			if (prop === 'file_reference') this.selected_node.setAttr('file_reference', val);
			
			if (prop === 'x_pct') this.selected_node.x(val / 100 * this.stage.width());
			if (prop === 'y_pct') this.selected_node.y(val / 100 * this.stage.height());
			
			this.layer.batchDraw();
		}

		async render_pdf_background() {
			if (!this.pdf_file) return;
			
			const url = frappe.urllib.get_full_url('/private/files/' + this.pdf_file);
			const loadingTask = pdfjsLib.getDocument(url);
			const pdf = await loadingTask.promise;
			const page = await pdf.getPage(1);
			
			const viewport = page.getViewport({ scale: 2 });
			const canvas = document.createElement('canvas');
			const context = canvas.getContext('2d');
			canvas.height = viewport.height;
			canvas.width = viewport.width;

			await page.render({ canvasContext: context, viewport: viewport }).promise;
			
			const img = new Image();
			img.src = canvas.toDataURL();
			img.onload = () => {
				const konvaImg = new Konva.Image({
					image: img,
					x: 0,
					y: 0,
					width: this.stage.width(),
					height: this.stage.height()
				});
				this.bg_layer.destroyChildren();
				this.bg_layer.add(konvaImg);
				this.bg_layer.draw();
			};
		}

		async save_layout() {
			const blocks = this.layer.find('.gpf-block').map(node => {
				return {
					block_type: node.attrs.type,
					x: (node.x() / this.stage.width()) * 100,
					y: (node.y() / this.stage.height()) * 100,
					width: (node.width() * node.scaleX() / this.stage.width()) * 100,
					height: (node.height() * node.scaleY() / this.stage.height()) * 100,
					// ... style and other fields
				};
			});

			await frappe.call({
				method: "gpf_builder.gpf_builder.api.api.save_layout",
				args: {
					blocks_json: JSON.stringify(blocks)
				}
			});
			frappe.show_alert("Layout saved successfully");
		}
	}

	// Initialize Builder
	frappe.require(["/assets/gpf_builder/js/lib/konva.min.js", "/assets/gpf_builder/js/lib/pdf.min.js"], function() {
		window.gpf_builder_instance = new GPFBuilder();
	});
};
