import frappe
from cycle_world.cycle_world.user_permissions.user import (
    add_user_permission,
    delete_existing_user_permissions,
    log_user_permission_creation,
)
def validate(doc, event=None):
    if(not doc.get('company')):
        return
    # is_parent_company = frappe.db.get_value('Company', doc.company, 'is_group')
    # if not is_parent_company:
    for i in doc.branch_users:
        if(i.user):
            delete_existing_user_permissions(i.user, doc.company, doc.name)
            perm = add_user_permission('Branch', doc.name, i.user, True, None, 1)
            if perm:log_user_permission_creation(doc.company, i.user, perm, doc.name)
    