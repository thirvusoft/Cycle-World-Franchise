frappe.provide('frappe.ui.form');

frappe.ui.form.ItemQuickEntryForm = frappe.ui.form.QuickEntryForm.extend({
	init: function(doctype, after_insert) {
		this._super(doctype, after_insert);
	},

	render_dialog: function() {
		this.mandatory = this.get_variant_fields().concat(this.mandatory);
        this.mandatory = this.mandatory.concat(this.get_fields());
		this.mandatory.splice(8,0,{fieldname:'cbb1',fieldtype:'Column Break'})
		this.on_changes()
		this._super();
		this.preset_fields_for_template();
		this.dialog.size = 'extra-large'
	},
	on_changes: function(){
		const me=this;	
		var additional_cost = 0, selling_cost = 0;	
		this.mandatory.forEach((df)=>{
			df.onchange=function(){
				if(df["fieldname"] == "ts_discount_" || df["fieldname"] == "ts_margin" || df["fieldname"] == "standard_buying_cost" || df["fieldname"] == "transportation_cost" || df["fieldname"] == "shipping_cost" || df["fieldname"] == "other_costs"){
					additional_cost = me.dialog.get_value('transportation_cost') + me.dialog.get_value('shipping_cost') + me.dialog.get_value('other_costs')
					selling_cost = me.dialog.get_value('standard_buying_cost') + additional_cost
					selling_cost = selling_cost + (selling_cost * me.dialog.get_value('ts_margin')) / 100
					selling_cost = selling_cost - (selling_cost * me.dialog.get_value('ts_discount_')) / 100
					me.dialog.fields_dict.additional_cost.set_value(additional_cost)
					me.dialog.fields_dict.standard_rate.set_value(selling_cost)
				}
				if(df["fieldname"] == "item_template"){
					me.render_attr_fields();
				}
			}
		})
	},
	render_attr_fields: function(){
			var selected = {}, me = this;
			var template = me.dialog.get_value('item_template')
			me.dialog.fields_dict.brand_name.set_value(template);
			me.dialog.fields_dict.variant_of.set_value(template);
			var fields = []
			me.field_names = []
			frappe.call({
				method:'cycle_world.cycle_world.custom.py.item.get_attributes',
				args:{
					template: template
				},
				async: false,
				callback(r){
					me.dialog.$wrapper.find('div[data-fieldname="attribute_html"]')[0].innerHTML = ''
					var brk_count = Math.round(r.message.length / 4) 
					r.message.forEach((attr, i)=>{
						if(i%brk_count==0 && (r.message.length -1) != i ){
							fields.push({
								fieldtype: 'Column Break',
								fieldname:frappe.scrub(`Column Break ${i}`)
							})
						}
						me.field_names.push(`cycle_${frappe.scrub(attr)}`)
						fields.push({
								fieldtype: 'Link',
								label: __(attr),
								options:'CW Item Attribute',
								fieldname:`cycle_${frappe.scrub(attr)}`,
								default:selected[attr],
								filters:{'item_attribute':attr},
								get_route_options_for_new_doc: function(field) {
									return  {
										'attribute_value':form.get_value(`cycle_${frappe.scrub(attr)}`),
										'item_attribute' : attr,
									}
								},
							})
					})
					me.form = new frappe.ui.FieldGroup({
						fields: fields,
						body: me.dialog.$wrapper.find('div[data-fieldname="attribute_html"]')[0]
					});
					me.form.make()					
				}
			})
			
	},
    get_fields: function() {
		this.get_field = [{
			fieldtype: 'Section Break',
			fieldname: "sbb1",
			label: "Item Attribute",
		},
		{
			fieldname: "attribute_html",
			fieldtype: "HTML",
			label: "Attributes",
		}
	];
		return this.get_field;
	},

	register_primary_action: function() {
		const me = this;
		this.dialog.set_primary_action(__('Save'), function() {

			var data = me.dialog.get_values();
			if (data) {
				me.form.fields.forEach(df => {
						data.attributes = me.set_attributes(me.dialog.get_value('item_template'), me.form,me.field_names)
				})	
				me.dialog.working = true;
				var values = me.update_doc();
				$.extend(data, values);
				me.insert(data);
			}
		});
	},

	insert: function(data) {
		let me = this;
		return new Promise(resolve => {
			frappe.call({
				method: "frappe.client.insert",
				args: {
					doc: data
				},
				callback: function(r) {
					me.dialog.hide();
					frappe.model.clear_doc(me.dialog.doc.doctype, me.dialog.doc.name);
					me.dialog.doc = r.message;
					if (frappe._from_link) {
						frappe.ui.form.update_calling_link(me.dialog.doc);
					} else {
						if (me.after_insert) {
							me.after_insert(me.dialog.doc);
						} else {
							// me.open_form_if_not_list();
						}
					}
				},
				error: function() {
					me.open_doc();
				},
				always: function() {
					me.dialog.working = false;
					resolve(me.dialog.doc);
				},
				freeze: true
			});
		});
	},

	get_variant_fields: function() {
		var variant_fields = [{
			fieldname: "create_variant",
			fieldtype: "Check",
			label: __("Create Variant"),
			default:1,
			hidden:1
		},
		{
			fieldname: 'item_template',
			label: __('Item Template'),
			reqd: 0,
			fieldtype: 'Link',
			options: "Item",
			get_query: function() {
				return {
					filters: {
						"has_variants": 1
					}
				};
			}
		},
		{
			fieldname:'cbb',
			fieldtype:'Column Break'
		}
	];

		return variant_fields;
	},

	preset_fields_for_template: function() {
		var for_variant = this.dialog.get_value('create_variant');

		let template_field = this.dialog.get_field("item_template");
		template_field.df.reqd = for_variant;
		template_field.set_value('');
		template_field.df.hidden = !for_variant;
		template_field.refresh();
		this.dialog.get_field("brand_name").df.hidden = this.dialog.get_value('create_variant');
		this.dialog.get_field("variant_of").df.hidden = this.dialog.get_value('create_variant');
		this.dialog.get_field("brand_name").refresh();
		this.dialog.get_field("variant_of").refresh();
		['item_code', 'item_name', 'is_stock_item', 'opening_stock','stock_uom'].forEach((d) => {
			let f = this.dialog.get_field(d);
			f.df.hidden = for_variant;
			f.refresh();
		});

		['item_code', 'stock_uom'].forEach((d) => {
			let f = this.dialog.get_field(d);
			f.df.reqd = !for_variant;
			f.refresh();
		});

	},
	set_attributes: function(template, form, field_names){
		var attr_tab = [];
		field_names.forEach((df)=>{
			var field = form.get_field(df)
			var value = form.get_value(df).split(' - ')[0]
			if(value){
				attr_tab.push({
					'cw_name':form.get_value(df),
					'variant_of':template,
					'attribute_value':value,
					'attribute':field.df.label
				})
			}
		})
		return(attr_tab)
	},
});
