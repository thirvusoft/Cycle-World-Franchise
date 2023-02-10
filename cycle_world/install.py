import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
    create_property_setter()
    make_custom_fields()

def create_property_setter():
    make_property_setter('Item', 'variant_of', 'read_only', 0, 'Check')
    make_property_setter('Item', 'item_code', 'reqd', 0, 'Check')
    make_property_setter('Item', 'naming_series', 'options', 'STO-ITEM-.YYYY.-\nTCW-.####', 'Text')
    make_property_setter('Item', 'naming_series', 'default', 'TCW-.####', 'Text')


def make_custom_fields():
    custom_field = {
        'Purchase Invoice':[
            {
            'fieldname':'land_cst_sc_brk',
            'fieldtype':'Section Break',
            'insert_after':'section_break_49',
            'label':'Landed Cost Voucher',
            'collapsible':1,
            'collapsible_depends_on':'eval:doc.update_stock',
            },
            {
            'fieldname':'distribute_charges_based_on',
            'label':'Distribute Charges Based On',
            'fieldtype':'Select',
            'options':frappe.get_meta('Landed Cost Voucher').get_field('distribute_charges_based_on').options,
            'insert_after':'land_cst_sc_brk'
            },
            {
            'fieldname':'landed_cost_taxes',
            'label':'Landed Cost',
            'fieldtype':'Table',
            'options':'Landed Cost Taxes and Charges',
            'description':'(Additional Cost includes in Item Valuation Rate)',
            'insert_after':'distribute_charges_based_on'
            },
            {
            'fieldname':'land_cst_sc_brk1',
            'fieldtype':'Section Break',
            'insert_after':'landed_cost_taxes'
            }
        ],
        'Purchase Receipt':[
            {
            'fieldname':'land_cst_sc_brk',
            'fieldtype':'Section Break',
            'insert_after':'total_taxes_and_charges',
            'label':'Landed Cost Voucher',
            'collapsible':1,
            'collapsible_depends_on':'eval:doc.company',
            },
            {
            'fieldname':'distribute_charges_based_on',
            'label':'Distribute Charges Based On',
            'fieldtype':'Select',
            'options':frappe.get_meta('Landed Cost Voucher').get_field('distribute_charges_based_on').options,
            'insert_after':'land_cst_sc_brk'
            },
            {
            'fieldname':'landed_cost_taxes',
            'label':'Landed Cost',
            'fieldtype':'Table',
            'options':'Landed Cost Taxes and Charges',
            'description':'(Additional Cost includes in Item Valuation Rate)',
            'insert_after':'distribute_charges_based_on'
            },
            {
            'fieldname':'land_cst_sc_brk1',
            'fieldtype':'Section Break',
            'insert_after':'landed_cost_taxes'
            }
        ],
        'Item Attribute Value':[
            {
                'fieldname':'old_value',
                'label':'Old Attribute Value',
                'fieldtype':'Data',
                'insert_after':'abbr',
                'read_only':1,
                'default':'',
            },
            {
                'fieldname':'old_abbr',
                'label':'Old Abbreviation',
                'fieldtype':'Data',
                'insert_after':'old_value',
                'read_only':1,
                'default':'',
            },
             {
                'fieldname':'curr_value',
                'label':'Current Attribute Value',
                'fieldtype':'Data',
                'read_only':1,
                'default':'',
                'insert_after':'old_abbr'
            },
        ],
        'Item Attribute':[
             {
                'fieldname':'last_changes',
                'label':'Recently Changed Attributes',
                'fieldtype':'Code',
                'read_only':1,
                'default':'[]',
                'insert_after':'item_attribute_values'
            },
        ]
    }
    create_custom_fields(custom_field)