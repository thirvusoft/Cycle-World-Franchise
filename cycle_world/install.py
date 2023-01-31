import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def after_install():
    create_property_setter()

def create_property_setter():
    make_property_setter('Item', 'variant_of', 'read_only', 0, 'Check')
    make_property_setter('Item', 'item_code', 'reqd', 0, 'Check')