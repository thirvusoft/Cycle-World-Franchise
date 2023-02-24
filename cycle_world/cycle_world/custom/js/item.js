frappe.ui.form.on('Item',{
	setup(frm){
		frm.set_query('variant_of', {
			filters: {
				'has_variants':1
			}
		});
		var attr_html = frm.$wrapper.find('div[data-fieldname="attribute_html"]')[0]
		attr_html.innerHTML = ''
		if(frm.doc.variant_of){
			var selected = {}
			if(!frm.is_new()){
				frm.doc.attributes.forEach((attr)=>{
					selected[attr.attribute] = attr.cw_name
				})
			}
			var fields = []
			var field_names = []
			frappe.call({
				method:'cycle_world.cycle_world.custom.py.item.get_attributes',
				args:{
					template:frm.doc.variant_of
				},
				callback(r){
					attr_html.innerHTML = ''
					var brk_count = Math.round(r.message.length / 4) 
					r.message.forEach((attr, i)=>{
						if(i%brk_count==0 && (r.message.length -1) != i ){
							fields.push({
								fieldtype: 'Column Break',
								fieldname:frappe.scrub(`Column Break ${i}`)
							})
						}
						field_names.push(`cycle_${frappe.scrub(attr)}`)
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
										'template':!frm.is_new()?frm.doc.name:''
									}
								},
							})
					})
					var form = new frappe.ui.FieldGroup({
						fields: fields,
						body: attr_html
					});
					form.make()
					let df = form.get_field('cycle_accessories')
					form.fields.forEach(df => {
						df.onchange =  function(){
							set_attributes(frm, form, field_names)
						}
					})					
				}
			})
			
		}
	},
	after_save(frm){
		// frm.reload_doc()
		var docname = frm.doc.name
		if(!frm.doc.variant_of){
			return
		}
		frappe.call({
			method:'cycle_world.cycle_world.custom.py.item.set_variant_name_for_manual_creation',
			args:{
				doc:frm.doc
			},
			async:false,
			callback(r){
				if(r.message.trim() == docname){
					frm.reload_doc()
					return
				}
				$(document).trigger("rename", ['Item', docname, r.message.trim()]);
				if (locals['Item'] && locals['Item'][docname]){
					delete locals['Item'][docname];
				}
				console.log('reload')
				frm.reload_doc();
			}
		})
	},
	refresh(frm){
		frm.trigger('setup')
	},
	onload(frm){
		frm.trigger('setup')
	},
	variant_of(frm){
		frm.trigger('setup')	
	},
	validate(frm){
		if(frm.doc.has_variants){
			frm.set_value('item_code', frm.doc.brand_name)
			frm.set_value('item_name', frm.doc.brand_name)
		}
	},
    brand_name: function(frm){
		// frm.set_value('item_code', frm.doc.brand_name)
		// frm.set_value('item_name', frm.doc.brand_name)
		frm.set_value('brand', frm.doc.brand_name)
		// frm.set_value('variant_of', frm.doc.brand_name)
	},
	standard_buying_cost(frm){
		item_price(frm)
	},
	transportation_cost(frm){
		item_price(frm)
	},
	shipping_cost(frm){
		item_price(frm)
	},
	other_costs(frm){
		item_price(frm)
	},
	ts_margin(frm){
		item_price(frm)
	},
	ts_discount_(frm){
		item_price(frm)
	},
})
function item_price(frm){
	var additional_cost = 0, selling_cost = 0;
	additional_cost = frm.doc.transportation_cost + frm.doc.shipping_cost + frm.doc.other_costs
	selling_cost = frm.doc.standard_buying_cost + additional_cost
	selling_cost = selling_cost + (selling_cost * frm.doc.ts_margin) / 100
	selling_cost = selling_cost - (selling_cost * frm.doc.ts_discount_) / 100
	frm.set_value('additional_cost', additional_cost)
	frm.set_value('standard_rate', selling_cost)
	frm.refresh_field('additional_cost')
	frm.refresh_field('standard_rate')
}
function set_attributes(frm, form, field_names){
	var attr_tab = [];
	field_names.forEach((df)=>{
		var field = form.get_field(df)
		var value = form.get_value(df).split(' - ')[0]
		if(value){
			attr_tab.push({
				'cw_name':form.get_value(df),
				'variant_of':frm.doc.variant_of,
				'attribute_value':value,
				'attribute':field.df.label
			})
		}
	})
	frm.set_value('attributes', attr_tab)
	frm.refresh_field('attributes')
}