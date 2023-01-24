import frappe
from erpnext.controllers.item_variant import (
	copy_attributes_to_variant, 
	generate_keyed_value_combinations,
	get_variant
	)
from six import string_types
import json
from frappe import _
from frappe.utils import cstr, flt



@frappe.whitelist()
def enqueue_multiple_variant_creation(item, args):
	# There can be innumerable attribute combinations, enqueue
	if isinstance(args, string_types):
		variants = json.loads(args)
		args = json.loads(args)
	for i in list(variants.keys()):
		if(len(variants[i]) == 0):
			del variants[i]
	for i in list(args.keys()):
		if(len(args[i]) == 0):
			del args[i]
	total_variants = 1
	for key in variants:
		total_variants *= len(variants[key])
	if total_variants >= 600:
		frappe.throw(_("Please do not create more than 500 items at a time"))
		return
	if total_variants < 10:
		return create_multiple_variants(item, args)
	else:
		frappe.enqueue(
			"erpnext.controllers.item_variant.create_multiple_variants",
			item=item,
			args=args,
			now=frappe.flags.in_test,
		)
		return "queued"

def create_multiple_variants(item, args):
	count = 0
	if isinstance(args, string_types):
		args = json.loads(args)

	args_set = generate_keyed_value_combinations(args)
	for attribute_values in args_set:
		if not get_variant(item, args=attribute_values):
			variant = create_variant(item, attribute_values)
			variant.save()
			count += 1

	return count

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
			"""select i.numeric_values, v.abbr, v.attribute_value, i.show_only_abbreviation_in_item_name
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
			cstr(attr.attribute_value) if item_attribute[0].numeric_values else item_attribute[0].attribute_value if not item_attribute[0].show_only_abbreviation_in_item_name else item_attribute[0].abbr
		)
		abbr_for_item_name.append(abbr_or_value_item_name)
	# abbreviations.insert(1, brand[:3:])
	# abbr_for_item_name.insert(1, brand)
	if abbreviations:
		variant.item_code = "{0}{1}".format(template_item_code.replace(" ",'')[:3:], "".join(abbreviations))
		variant.item_name = "{0} {1}".format(template_item_name, " ".join(abbr_for_item_name))