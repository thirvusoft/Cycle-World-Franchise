frappe.ui.form.on('Item',{
    brand_name: function(frm){
		frm.set_value('item_code', frm.doc.brand_name)
		frm.set_value('item_name', frm.doc.brand_name)
		frm.set_value('brand', frm.doc.brand_name)
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