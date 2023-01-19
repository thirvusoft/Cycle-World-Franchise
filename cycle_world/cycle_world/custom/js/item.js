frappe.ui.form.on('Item',{
    brand_name: function(frm){
		frm.set_value('item_code', frm.doc.brand_name)
		frm.set_value('item_name', frm.doc.brand_name)
		frm.set_value('brand', frm.doc.brand_name)
	},
})