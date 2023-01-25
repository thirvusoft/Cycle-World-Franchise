import frappe
from frappe import _

def add_user_permission(
    doctype,
    name,
    user,
    ignore_permissions=False,
    applicable_for=None,
    is_default=0,
    hide_descendants=0,
    ):
    """Add user permission"""
    from frappe.core.doctype.user_permission.user_permission import user_permission_exists

    if not user_permission_exists(user, doctype, name, applicable_for):
        if not frappe.db.exists(doctype, name):
            frappe.throw(_("{0} {1} not found").format(_(doctype), name), frappe.DoesNotExistError)

        doc=frappe.get_doc(
            dict(
                doctype="User Permission",
                user=user,
                allow=doctype,
                for_value=name,
                is_default=is_default,
                applicable_for=applicable_for,
                apply_to_all_doctypes=0 if applicable_for else 1,
                hide_descendants=hide_descendants,
            ))
        doc.insert(ignore_permissions=ignore_permissions)
        return doc.name

def validate(doc, event=None):
    if(not doc.get('company')):
        return
    is_parent_company = frappe.db.get_value('Company', doc.company, 'is_group')
    if not is_parent_company:
        delete_existing_user_permissions(doc.name, doc.company)
        perm = add_user_permission('Company', doc.company, doc.name, True, None, 1)
        if perm:log_user_permission_creation(doc.company, doc.name, perm)

def log_user_permission_creation(company:str, user:str, perm:str, branch:str=None):
    log = frappe.get_doc({
        'doctype':'Auto Created User Permission',
        'user':user,
        'company':company,
        'user_perm_doc_name':perm,
        'branch':branch or '',
    })
    log.insert(ignore_permissions = True)

def delete_existing_user_permissions(user:str, company:str, branch:str=None):
    perms = frappe.db.get_all('Auto Created User Permission', filters={'user':user, 'company':company, 'branch':branch}, fields=['name', 'user_perm_doc_name'])
    for i in perms:
        frappe.delete_doc_if_exists('Auto Created User Permission', i['name'])
        frappe.delete_doc_if_exists('User Permission', i['user_perm_doc_name'])