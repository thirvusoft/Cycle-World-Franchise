# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


class OnlineSalesSeries(Document):
	def validate(self):
		if(not self.is_new()):
			old_series = self._doc_before_save.abbreviation
			self.delete_naming_series_options(old_series)
		self.add_naming_series_options(self.abbreviation)

	def on_trash(self):
		self.delete_naming_series_options(self.abbreviation)
	def add_naming_series_options(self, option=''):
		if(not option):return
		make_property_setter(
				'Sales Invoice',
				"naming_series",
				"options",
				frappe.get_meta('Sales Invoice').get_field('naming_series').options+"\n"+option,
				"Text",
			)
	def delete_naming_series_options(self, option=''):
		if(not option):return
		options = frappe.db.get_value('Property Setter',
				{
					'doc_type':'Sales Invoice',
					'field_name':"naming_series",
					'property':"options",
					'value':['like', '%'+option+'%'],
					'property_type':"Text"
				},
				'value'
			)
		if(not options):
			return
		name = frappe.db.get_value('Property Setter',
				{
					'doc_type':'Sales Invoice',
					'field_name':"naming_series",
					'property':"options",
					'value':['like', option],
					'property_type':"Text"
				},
				'name'
			) 
		options = options.split('\n')
		if(option not in options):
			return
		frappe.delete_doc_if_exists('Property Type', name)
		idx = options.index(option)
		options = options[:idx:]+options[idx+1::]
		options = "\n".join(options)
		make_property_setter(
				'Sales Invoice',
				"naming_series",
				"options",
				options,
				"Text",
			)
	@frappe.whitelist()
	def preview_series(self, abbr) -> str:
		"""Preview what the naming series will generate."""

		generated_names = []
		series = abbr
		try:
			doc = _fetch_last_doc_if_available()
			for _count in range(3):
					generated_names.append(make_autoname(series, doc=doc))
		except Exception as e:
			if frappe.message_log:
				frappe.message_log.pop()
			return _("Failed to generate names from the series") + f"\n{str(e)}"

		# Explcitly rollback in case any changes were made to series table.
		frappe.db.rollback()  # nosemgrep
		return "\n".join(generated_names)

def _fetch_last_doc_if_available(doctype="Sales Invoice"):
	"""Fetch last doc for evaluating naming series with fields."""
	try:
		return frappe.get_last_doc(doctype)
	except Exception:
		return None
	