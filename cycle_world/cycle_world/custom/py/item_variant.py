import frappe
from erpnext.controllers.item_variant import copy_attributes_to_variant
from six import string_types
import json
from frappe.utils import cstr, flt


@frappe.whitelist()
def create_variant(item, args):
	if isinstance(args, string_types):
		args = json.loads(args)

	template = frappe.get_doc("Item", item)
	variant = frappe.new_doc("Item")
	variant.variant_based_on = "Item Attribute"
	variant_attributes = []

	for d in template.attributes:
		variant_attributes.append({"attribute": d.attribute, "attribute_value": args.get(d.attribute)})

	variant.set("attributes", variant_attributes)
	copy_attributes_to_variant(template, variant)
	make_variant_item_code(template.item_code, template.item_name, variant)

	return variant

def make_variant_item_code(template_item_code, template_item_name, variant):
	"""Uses template's item code and abbreviations to make variant's item code"""
	brand = frappe.db.get_value('Item', template_item_code, 'brand') or ''
	if variant.item_code:
		return

	abbreviations, abbr_for_item_name = [], []
	for attr in variant.attributes:
		item_attribute = frappe.db.sql(
			"""select i.numeric_values, v.abbr, v.attribute_value
			from `tabItem Attribute` i left join `tabItem Attribute Value` v
				on (i.name=v.parent)
			where i.name=%(attribute)s and (v.attribute_value=%(attribute_value)s or i.numeric_values = 1)""",
			{"attribute": attr.attribute, "attribute_value": attr.attribute_value},
			as_dict=True,
		)

		if not item_attribute:
			continue
			# frappe.throw(_('Invalid attribute {0} {1}').format(frappe.bold(attr.attribute),
			# 	frappe.bold(attr.attribute_value)), title=_('Invalid Attribute'),
			# 	exc=InvalidItemAttributeValueError)

		abbr_or_value = (
			cstr(attr.attribute_value) if item_attribute[0].numeric_values else item_attribute[0].abbr
		)
		abbreviations.append(abbr_or_value)

		abbr_or_value_item_name = (
			cstr(attr.attribute_value) if item_attribute[0].numeric_values else item_attribute[0].attribute_value
		)
		abbr_for_item_name.append(abbr_or_value_item_name)
	abbreviations.insert(1, brand[:3:])
	abbr_for_item_name.insert(1, brand[:3:])
	if abbreviations:
		variant.item_code = "{0}".format("".join(abbreviations))
		variant.item_name = "{0}".format(" ".join(abbr_for_item_name))

