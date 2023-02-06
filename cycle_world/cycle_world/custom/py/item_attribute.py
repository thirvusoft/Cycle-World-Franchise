import frappe
from cycle_world.cycle_world.custom.py.item import set_variant_name_for_manual_creation

def validate(self, event=None):
    changed_attributes = {}
    for i in self.item_attribute_values:
        if not frappe.db.exists('CW Item Attribute', {'attribute_value':i.old_value, 'item_attribute':self.name, 'abbr':i.old_abbr} or not i.old_value):
            doc = frappe.get_doc({
                'doctype':'CW Item Attribute',
                'attribute_value':i.old_value or i.attribute_value,
                'abbr':i.old_abbr or i.abbr,
                'item_attribute':self.name
            })
            doc.save()
            i.old_value = i.attribute_value
            i.old_abbr = i.abbr
        elif(i.attribute_value != i.old_value or i.abbr != i.old_abbr):
            changed_attributes[i.attribute_value] = i.old_value
            cw = frappe.get_doc('CW Item Attribute', {
            'abbr':i.old_abbr,
            'attribute_value':i.old_value,
            'item_attribute':self.name
            })
            cw.update_cw_attributes({'abbr':i.abbr, 'attribute_value':i.attribute_value})
            i.old_value = i.attribute_value
            i.old_abbr = i.abbr
    items = frappe.db.get_all("Item Variant Attribute", filters={'parenttype':'Item', 'attribute':self.name, 'attribute_value':['in', list(changed_attributes.keys())]}, pluck='parent')
    for i in items:
        doc = frappe.get_doc('Item', i)
        set_variant_name_for_manual_creation(doc)