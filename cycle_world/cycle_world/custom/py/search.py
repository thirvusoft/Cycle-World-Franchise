import frappe
from frappe import _, is_whitelisted
from frappe.desk.search import (
    search_widget, 
    build_for_autosuggest
    )

@frappe.whitelist()
def search_link(
	doctype,
	txt,
	query=None,
	filters=None,
	page_length=5,
	searchfield='name',
	reference_doctype=None,
	ignore_user_permissions=False,
):
    if(doctype!='Item'):
        search_widget(
            doctype,
            txt.strip(),
            query,
            searchfield=searchfield,
            page_length=page_length,
            filters=filters,
            reference_doctype=reference_doctype,
            ignore_user_permissions=ignore_user_permissions,
        )
        frappe.response["results"] = build_for_autosuggest(frappe.response["values"])
        del frappe.response["values"]
    else:
        start=0
        as_dict=False
        try:
            frappe.response["values"] = frappe.call(
                "cycle_world.cycle_world.custom.py.item.item_query", doctype, txt, searchfield, start, page_length, filters, as_dict=as_dict
            )
            frappe.response["results"] = build_for_autosuggest(frappe.response["values"])
            del frappe.response["values"]
        except frappe.exceptions.PermissionError as e:
            if frappe.local.conf.developer_mode:
                raise e
            else:
                frappe.respond_as_web_page(
                    title="Invalid Method", html="Method not found", indicator_color="red", http_status_code=404
                )
            return
        except Exception as e:
            raise e