# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CWItemAttribute(Document):
	def autoname(self):
		self.name = f"{self.attribute_value} - {self.abbr}"
		if(frappe.db.exists('CW Item Attribute', self.name)):
			self.name = f"{self.attribute_value} - {self.abbr} - {self.item_attribute.split(' ')[0]}"
