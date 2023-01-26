import frappe
from frappe.model.rename_doc import update_document_title
from frappe.utils import cstr, flt

def get_all_template():
	ig = frappe.db.get_value('Item Attribute', {'is_item_group':1}, 'name')
	temp = frappe.db.get_all('Item', filters={'has_variants':1}, pluck='name')
	frappe.errprint(temp)
	names = []
	for i in temp:
		variants = frappe.db.get_all('Item', filters={'variant_of':i}, pluck='name')
		for j in variants:
			doc = frappe.get_doc('Item', j)
			name = make_variant_item_code(i, i, doc, ig)
			if name:
				names.append(name)
	print(names, len(names))
	print(list(set(names)), len(list(set(names))))

def make_variant_item_code(template_item_code, template_item_name, variant, item_group):
	"""Uses template's item code and abbreviations to make variant's item code"""

	attributes = [i.attribute for i in variant.attributes]
	if(item_group not in attributes):
		return
	print(template_item_code, 'Passed')
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
			
		if(attr.attribute != item_group):
			abbr_or_value = (
				cstr(attr.attribute_value) if item_attribute[0].numeric_values else item_attribute[0].abbr
			)
			abbreviations.append(abbr_or_value)

			abbr_or_value_item_name = (
				cstr(attr.attribute_value) if item_attribute[0].numeric_values else item_attribute[0].attribute_value if not item_attribute[0].show_only_abbreviation_in_item_name else item_attribute[0].abbr
			)
			abbr_for_item_name.append(abbr_or_value_item_name)
		else:
			frappe.errprint(attr.attribute_value)
			variant.update({
				'item_group':attr.attribute_value
			})

	new_ic = "{0}{1}".format(template_item_code.replace(" ",'')[:3:], "".join(abbreviations))
	new_in = "{0} {1}".format(template_item_name, " ".join(abbr_for_item_name))
	frappe.errprint(variant.item_group)
	variant.save()
	# print('Item', variant.name, 'item_name', variant.item_name, new_in, new_ic, variant.variant_of)
	print(variant.item_name, "||", new_in, "||",variant.item_code, "||", new_ic,'||', variant.item_group)
	update_document_title('Item', variant.name, 'item_name', variant.item_name, new_in, new_ic)
	return new_ic
	
	


def set_item_tax_rate():
	for i in frappe.get_all('Item Tax', pluck='name', filters={'parenttype':'Item'}):
		frappe.delete_doc('Item Tax', i)
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
