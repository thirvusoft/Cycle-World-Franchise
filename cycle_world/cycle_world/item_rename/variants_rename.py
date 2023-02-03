import frappe
from frappe.model.rename_doc import update_document_title
from frappe.utils import cstr, flt

def get_all_template():
	ig = frappe.db.get_value('Item Attribute', {'is_item_group':1}, 'name')
	temp = frappe.db.get_all('Item', filters={'has_variants':1, 'name':'G SPORTS'}, pluck='name')
	names = []
	print(temp)
	for i in temp:
		variants = frappe.db.get_all('Item', filters={'variant_of':i, 'name':'GSP26ZRVBRFSKDSSGRY'}, pluck='name')
		print(variants)
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
	# if(item_group not in attributes):
	# 	return
	print(template_item_code, 'Passed')
	abbreviations, abbr_for_item_name = [], []
	for attr in variant.attributes:
		item_attribute = frappe.db.sql(
			"""select i.numeric_values, v.abbr, v.attribute_value, i.show_only_abbreviation_in_item_name,i.prefix ,i.suffix
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
			cstr(attr.attribute_value) if item_attribute[0].numeric_values else (item_attribute[0].prefix or "") + item_attribute[0].abbr + (item_attribute[0].suffix or "")
			)
			abbreviations.append(abbr_or_value)

			abbr_or_value_item_name = (
				cstr(attr.attribute_value) if item_attribute[0].numeric_values else  (item_attribute[0].prefix or "" ) + item_attribute[0].attribute_value + (item_attribute[0].suffix or "") if not item_attribute[0].show_only_abbreviation_in_item_name else (item_attribute[0].prefix or "") + item_attribute[0].abbr + (item_attribute[0].suffix or "")
			)
			abbr_for_item_name.append(abbr_or_value_item_name)
		else:
			variant.update({
				'item_group':attr.attribute_value
			})

	new_ic = "{0}{1}".format(template_item_code.replace(" ",'')[:3:], "".join(abbreviations))
	new_in = "{0} {1}".format(template_item_name, " ".join(abbr_for_item_name))
	variant.save()
	# print('Item', variant.name, 'item_name', variant.item_name, new_in, new_ic, variant.variant_of)
	print(variant.item_name, "||", new_in, "||",variant.item_code, "||", new_ic,'||', variant.item_group)
	update_document_title('Item', variant.name, 'item_name', variant.item_name, new_in, new_in, new_ic)
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

def update_brand_in_item_attributes():
	"""Update brand field in item attributes which name like 'Model' """
	import re
	model_attr = frappe.db.get_all('Item Attribute', filters={'name':['like', '%model%']}, pluck='name')
	print(model_attr, len(model_attr))
	s=f=0
	flrs = []
	for i in model_attr:
		txt = re.split("model", i, flags=re.IGNORECASE)[0]
		print(txt, 1111)
		if(frappe.db.exists('Brand', {'name':txt})):
			s+=1
			frappe.db.set_value('Item Attribute', i, 'brand', txt)
		else:
			f+=1
			flrs.append(i)
			print('Unsuccessful Attribute: ', i)
	print(f"Successfull: {s}\nUnsuccessfull: {f}")
	print('Failures: ',flrs)

def create_attributes_in_new_doctype():
	doctype = 'CW Item Attribute'
	it_at = frappe.db.get_all('Item Attribute', pluck='name')
	tot_count = 0
	invalid = []
	for i in it_at:
		val = frappe.db.get_all('Item Attribute Value', filters={'parent':i}, fields=['attribute_value', 'abbr'])
		tot_count += len(val)
		for j in val:
			doc = frappe.get_doc({
				'doctype':doctype,
				'attribute_value':j['attribute_value'],
				'abbr':j['abbr'],
				'item_attribute':i,
				'from_bulk_create':1
			})
			# try:
			doc.save()
			# except:
			# 	invalid.append(j['attribute_value'])
	print(f'Total Doc Count: {tot_count}\nInvalid: {invalid}')

def update_old_attribute_table_in_item():
	var_attr = frappe.db.get_all('Item Variant Attribute', filters={'parenttype':'Item'}, fields=['name', 'attribute', 'attribute_value'])
	for i in var_attr:
		doc = frappe.get_doc('Item Variant Attribute', i['name'])
		cw_name = frappe.db.get_value('CW Item Attribute', filters={'item_attribute':i['attribute'], 'attribute_value':i['attribute_value']})
		doc.update({
			'cw_name':cw_name
		})
		doc.save()