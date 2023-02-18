# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

from cycle_world.cycle_world.custom.py.item import autoname
import frappe
from frappe.model.document import Document
from frappe.model.rename_doc import update_document_title


class CWItemAttribute(Document):
	def autoname(self):
		name = f"{self.attribute_value} - {self.abbr}"
		self.name = f"{self.attribute_value} - {self.abbr}"
			
		if(frappe.db.exists('CW Item Attribute', self.name)):
				self.name = f"{self.attribute_value} - {self.abbr} - {self.item_attribute.split(' ')[0]}"
			

	def after_insert(self):
		if(self.from_bulk_create):
			return
		if(not self.get('from_item_attribute')):
			doc = frappe.new_doc('Item Attribute Value')
			idx = frappe.db.get_value('Item Attribute Value', {
				'parent':self.item_attribute,
				'parentfield':'item_attribute_values',
				'parenttype': "Item Attribute",
			}, 'idx', order_by = 'idx desc') or 0
			doc.update({
				'parent':self.item_attribute,
				'parentfield':'item_attribute_values',
				'parenttype': "Item Attribute",
				'abbr': self.abbr,
				'attribute_value': self.attribute_value,
				'idx':idx+1,
				'old_value':self.attribute_value,
				'abbr': self.abbr,
			})
			doc.save()
	
	def update_cw_attributes(self, changed_values):
		self.update({
			'abbr':changed_values.get('abbr') or '',
			'attribute_value':changed_values.get('attribute_value') or ''
		})
		self.save()
		self.reload()
		old_name = self.name
		self.autoname()
		update_document_title(doctype="CW Item Attribute", docname=old_name, new_name=self.name)
		attrs = frappe.db.get_all("Item Variant Attribute", {'parenttype':'Item', 'attribute':self.item_attribute, 'attribute_value':changed_values.get('old_value')}, pluck ='name')
		for i in attrs:
			frappe.db.set_value("Item Variant Attribute", i, 'cw_name', self.name)
