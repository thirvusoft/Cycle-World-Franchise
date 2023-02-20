frappe.ui.form.on('Company',{
    refresh: function(frm){
        frm.set_query("default_landed_cost_account", function() {
            return {
                filters: {
                    "account_type": ['in', ["Tax", "Chargeable", "Income Account", "Expenses Included In Valuation", "Expenses Included In Asset Valuation"]],
                    "company": frm.doc.company
                }
            };
        });
    },
})