frappe.ui.form.on('Purchase Receipt',{
    refresh: function(frm){
        frm.set_query("expense_account", 'landed_cost_taxes', function() {
            return {
                filters: {
                    "account_type": ['in', ["Tax", "Chargeable", "Income Account", "Expenses Included In Valuation", "Expenses Included In Asset Valuation"]],
                    "company": frm.doc.company
                }
            };
        });
    },
    validate: function(frm,cdt,cdn){
        for(var i=0;i<frm.doc.items.length;i++){
            console.log(frm.doc.items[i].item_code)
            if(frm.doc.items[i].item_code){
                frappe.db.get_doc('Item', frm.doc.items[i].item_code).then((d) => {
                    if(d.standard_buying_cost != frm.doc.items[i].rate){
                        frappe.db.set_value("Item",frm.doc.items[i].item_code,"standard_buying_cost",frm.doc.items[i].rate)
                    }
                })
            }
        }
    }

});
// frappe.ui.form.on('Purchase Receipt Item',{
//     rate: function(frm,cdt,cdn){
//         var rows = locals[cdt][cdn]
//         if(rows.item_code){
//             frappe.db.get_doc('Item', rows.item_code).then((doc) => {
//                 console.log(doc.standard_buying_cost)
//                 if(doc.standard_buying_cost != rows.rate){
//                     frappe.db.set_value("Item",rows.item_code,"standard_buying_cost",rows.rate)
//                 }
//             })
//         }
//     }
// });