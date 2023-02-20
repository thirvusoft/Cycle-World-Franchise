frappe.ui.form.on('Contact',{
    refresh: function(frm){
        frm.remove_custom_button( "Invite as User");
       
    }})