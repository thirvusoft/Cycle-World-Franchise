import frappe

def validate(self, event):
    for i in self.item_attribute_values:
        if not frappe.db.exists('CW Item Attribute', {'attribute_value':i.attribute_value, 'item_attribute':self.name}):
            doc = frappe.get_doc({
                'doctype':'CW Item Attribute',
                'attribute_value':i.attribute_value,
                'abbr':i.abbr,
                'item_attribute':self.name
            })
            doc.save()