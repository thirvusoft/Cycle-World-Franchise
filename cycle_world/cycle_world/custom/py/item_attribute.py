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
                'item_attribute':self.name,
                'from_item_attribute':1
            })
            doc.save()
            i.old_value = i.attribute_value
            i.old_abbr = i.abbr
        elif(i.attribute_value != i.old_value or i.abbr != i.old_abbr):
            changed_attributes[i.old_value] = i.attribute_value
            cw = frappe.get_doc('CW Item Attribute', {
            'abbr':i.old_abbr,
            'attribute_value':i.old_value,
            'item_attribute':self.name
            })
            cw.update_cw_attributes({'abbr':i.abbr, 'attribute_value':i.attribute_value, 'old_value':i.old_value})
            i.old_value = i.attribute_value
            i.old_abbr = i.abbr
    items = frappe.db.get_all("Item Variant Attribute", filters={'variant_of':['is', 'set'], 'parenttype':'Item', 'attribute':self.name, 'attribute_value':['in', list(changed_attributes.keys())]}, pluck='parent')
    self.last_changes = f"{items}"
    for j in items:
        for i in list(changed_attributes.keys()):
            name = frappe.db.get_value("Item Variant Attribute", {'parenttype':'Item', 'attribute':self.name, 'attribute_value':i, 'parent':j},'name')
            if(name):
                frappe.db.set_value("Item Variant Attribute", name, 'attribute_value', changed_attributes[i])
        

    
@frappe.whitelist()
def after_save(items = '[]'):
    items = eval(items)
    total = len(items)
    count=0
    for i in items:
        count += 1
        doc = frappe.get_doc('Item', i)
        set_variant_name_for_manual_creation(doc)
        frappe.publish_progress(count / total * 100, title=("Updating Variants..."), description=doc.name)