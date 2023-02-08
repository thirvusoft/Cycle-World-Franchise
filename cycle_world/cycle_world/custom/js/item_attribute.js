let cw_names = [];
frappe.ui.form.on('Item Attribute',{
    setup: function(frm){
        if(frm.is_new())return
        setTimeout(()=>{
            frm.fields_dict.item_attribute_values.$wrapper.find('.grid-remove-rows').on('click', ()=>{
                var selected = frm.get_selected().item_attribute_values || []
                selected.forEach(r =>{
                    var row = locals['Item Attribute Value'][r]
                    frappe.db.get_value('CW Item Attribute', {'attribute_value':row.attribute_value, 'item_attribute':frm.doc.name}, 'name').then(res => {
                        cw_names.push(res.message.name)
                    })
                })
                
            }) 
        }, 1000)
        
    },
    after_save(frm){
        frappe.call({
            method:"cycle_world.cycle_world.custom.py.item_attribute.after_save",
            args:{
                items:frm.doc.last_changes
            }
        })
    },
    refresh: function(){
        cw_names = [];
    },
    validate: function(frm){
        cw_names.forEach(cw => {
            frappe.db.delete_doc('CW Item Attribute', cw)
        })
    }
  }) 