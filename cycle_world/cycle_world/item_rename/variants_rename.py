import frappe
from frappe.model.rename_doc import update_document_title

def get_all_template():
	temp = frappe.db.get_all('Item', filters={'has_variants':1}, pluck='name')
	print(temp)
	for i in temp:
		variants = frappe.db.get_all('Item', filters={'variant_of':i}, pluck='name')
		print(variants)
		for j in variants:
			doc = frappe.get_doc('Item', j)
			make_variant_item_code(i, i, doc)

def make_variant_item_code(template_item_code, template_item_name, variant):
	"""Uses template's item code and abbreviations to make variant's item code"""
	brand = frappe.db.get_value('Item', template_item_code, 'brand') or ''
	# if variant.item_code:
	# 	return

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
	abbreviations.insert(1, brand.replace(' ', '')[:3:])
	abbr_for_item_name.insert(1, brand.replace(' ', '')[:3:])
	# if abbreviations:
	# 	variant.item_code = "{0}".format("".join(abbreviations))
	# 	variant.item_name = "{0}".format(" ".join(abbr_for_item_name))
	new_ic = "".join(abbreviations)
	new_in = " ".join(abbr_for_item_name)
	update_document_title('Item', variant.name, 'item_name', variant.item_name, new_in, new_ic)
	print('Item', variant.name, 'item_name', variant.item_name, new_in, new_ic)


def set_item_tax_rate():
	temp = frappe.db.get_all('Item', filters={'has_variants':1}, pluck='name')
	for i in temp:
		pp = frappe.get_doc({
			'doctype': "Item Tax",
			'item_tax_template': "GST 12% - PP",
			'parent': i,
			'parentfield': "taxes",
			'parenttype': "Item",
		})
		cy = frappe.get_doc({
			'doctype': "Item Tax",
			'item_tax_template': "GST 12% - TCW",
			'parent': i,
			'parentfield': "taxes",
			'parenttype': "Item",
		})
		pp.insert()
		cy.insert()
