frappe.ui.form.on('Branch',{
    setup(frm){
        frappe.call({
            method:"cycle_world.cycle_world.custom.py.sales_invoice.get_invoice_series_options",
            callback(r){
                frm.set_df_property('select_invoice_series', 'options', r.message)
            }
        })
    }
})