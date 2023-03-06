frappe.ui.form.on('Stock Reconciliation',{
    refresh(frm){
        frm.add_custom_button('Fetch Item Based on Item Code', ()=>{
            frappe.call({
                method: 'cycle_world.cycle_world.item_rename.variants_rename.get_item_name_based_on_item_code',
                args:{
                    doc:frm.doc
                },
                freeze:true,
                callback(r){
                    frm.set_value('items', r.message)
                }
            })
        })
    }
})