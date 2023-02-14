frappe.ui.form.on('Purchase Invoice',{
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
    on_submit: function(frm){
        frappe.call({
            method: 'cycle_world.cycle_world.custom.py.item.update_item_price_from_purchase',
            args:{
                items:frm.doc.items
            }
        })
        
    }
});