import frappe
from frappe.model.rename_doc import update_document_title
from frappe.utils import cstr, flt

def get_all_template():
	ig = frappe.db.get_value('Item Attribute', {'is_item_group':1}, 'name')
	temp = frappe.db.get_all('Item', filters={'has_variants':1, }, pluck='name')
	names = []
	print(temp)
	for i in temp:
		variants = frappe.db.get_all('Item', filters={'variant_of':i}, pluck='name')
		print(variants)
		for j in variants:
			doc = frappe.get_doc('Item', j)
			name = make_variant_item_code(i, i, doc, ig)
			if name:
				names.append(name)
		frappe.db.commit()
	print(names, len(names))
	print(list(set(names)), len(list(set(names))))

def make_variant_item_code(template_item_code, template_item_name, variant, item_group):
	"""Uses template's item code and abbreviations to make variant's item code"""

	# attributes = [i.attribute for i in variant.attributes]
	# # if(item_group not in attributes):
	# # 	return
	# print(template_item_code, 'Passed')
	# abbreviations, abbr_for_item_name = [], []
	# for attr in variant.attributes:
	# 	item_attribute = frappe.db.sql(
	# 		"""select i.numeric_values, v.abbr, v.attribute_value, i.show_only_abbreviation_in_item_name,i.prefix ,i.suffix
	# 		from `tabItem Attribute` i left join `tabItem Attribute Value` v
	# 			on (i.name=v.parent)
	# 		where i.name=%(attribute)s and (v.attribute_value=%(attribute_value)s or i.numeric_values = 1)""",
	# 		{"attribute": attr.attribute, "attribute_value": attr.attribute_value},
	# 		as_dict=True,
	# 	)

	# 	if not item_attribute:
	# 		continue
			
	# 	if(attr.attribute != item_group):
	# 		abbr_or_value = (
	# 		cstr(attr.attribute_value) if item_attribute[0].numeric_values else (item_attribute[0].prefix or "") + item_attribute[0].abbr + (item_attribute[0].suffix or "")
	# 		)
	# 		abbreviations.append(abbr_or_value)

	# 		abbr_or_value_item_name = (
	# 			cstr(attr.attribute_value) if item_attribute[0].numeric_values else  (item_attribute[0].prefix or "" ) + item_attribute[0].attribute_value + (item_attribute[0].suffix or "") if not item_attribute[0].show_only_abbreviation_in_item_name else (item_attribute[0].prefix or "") + item_attribute[0].abbr + (item_attribute[0].suffix or "")
	# 		)
	# 		abbr_for_item_name.append(abbr_or_value_item_name)
	# 	else:
	# 		variant.update({
	# 			'item_group':attr.attribute_value
	# 		})

	# new_ic = "{0}{1}".format(template_item_code.replace(" ",'')[:3:], "".join(abbreviations))
	# new_in = "{0} {1}".format(template_item_name, " ".join(abbr_for_item_name))
	# variant.save()
	# # print('Item', variant.name, 'item_name', variant.item_name, new_in, new_ic, variant.variant_of)
	# print(variant.item_name, "||", new_in, "||",variant.item_code, "||", new_ic,'||', variant.item_group)
	update_document_title('Item', variant.name, 'item_name', variant.item_name, variant.item_name, variant.item_name)
	return "new_ic"
	


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

def copy_old_attribute_value():
	for i in frappe.db.get_all('Item Attribute Value', fields=['name', 'attribute_value', 'abbr']):
		frappe.db.set_value('Item Attribute Value', i['name'], 'old_value', i['attribute_value'])
		frappe.db.set_value('Item Attribute Value', i['name'], 'old_abbr', i['abbr'])
		frappe.db.set_value('Item Attribute Value', i['name'], 'curr_value', i['attribute_value'])

def check_attributes_existance():
	attr = frappe.get_all('Item Attribute', pluck='name')
	non_exist = []
	attr_dict = {}
	tot_val = []
	for i in attr:
		val = frappe.get_all('Item Attribute Value', filters={'parent':i}, pluck='attribute_value')
		tot_val += val
		item_var_val = frappe.get_all('Item Variant Attribute', filters={'attribute':i, 'attribute_value':['not in',val], 'variant_of':['is', 'set'], 'cw_name':['is', 'not set']}, pluck='attribute_value')
		item_variants = frappe.get_all('Item Variant Attribute', filters={'attribute':i, 'attribute_value':['not in',val], 'variant_of':['is', 'set'], 'cw_name':['is', 'not set']}, fields=['attribute_value', 'name', 'parent'])
		
		for i in item_variants:
			if(i['attribute_value'] not in list(attr_dict.keys())):
				attr_dict[i['attribute_value']]=[[i['name'], i['parent']]]
			else:
				attr_dict[i['attribute_value']].append([i['name'], i['parent']])


		if(len(item_var_val)):
			non_exist+=list(set(item_var_val))
	print('Attr Dict: ', attr_dict)
	print('Non Existing Values: ', non_exist)
	a = [i for i in non_exist if(i not in tot_val)]
	print('Final: ',a)
	# return
	for i in a:
		like = frappe.get_value('Item Attribute Value', {'attribute_value':['like', i]}, 'attribute_value')
		if(like):
			print(i,like, len(i), len(like))
			cw_name = frappe.db.get_value('CW Item Attribute', {'attribute_value':like}, 'name')
			for j in attr_dict[i]:
				frappe.db.set_value('Item Variant Attribute', j, 'attribute_value', like)
				frappe.db.set_value('Item Variant Attribute', j, 'cw_name', cw_name)
				print(j)		
	map_ = {'INNER':'-INNER', 'OUTER':'-OUTER', 'DISC CABLE-2050MM':'-DISC(2050MM)','INNER&OUTER':'-INNER&OUTER', 'M.GRY/YELLOW':'M.GREY/YELLOW','M.ORANG':'M.ORANGE','ORANG/GRY':'ORANGE/GREY', 'SIL/M.ORANG':'SIL/M.ORANGE','BLACK/ORANG':'BLACK/ORANGE', 'GRAY/BLUE':'GREY/BLUE', 'GRY/ORANG':'GREY/ORANGE', 'PINK/GRAY':'PINK/GREY', 'M.GR/M.GREEN':'M.GREY/M.GREEN', 'M RED / BLACK':'M.RED / BLACK', 'M.GRY/ORANG':'M.GREY/ORANGE', 'BASKET-ADULT':'ADULT', 'BASKET-KIDS':'KIDS'}
	for i in map_:
		var = frappe.get_all('Item Variant Attribute', filters={'attribute_value':i}, pluck='name')
		cw_name = frappe.db.get_value('CW Item Attribute', {'attribute_value':map_[i]}, 'name')
		for j in var:
			print(cw_name, i)
			frappe.db.set_value('Item Variant Attribute', j, 'attribute_value', map_[i])
			frappe.db.set_value('Item Variant Attribute', j, 'cw_name', cw_name)

def update_item_to_naming_series():
	frappe.db.sql('''Update `tabSeries` set current=2355 where name="TCW-";''')
	counter = frappe.db.sql("""
				select current from `tabSeries` where name='TCW-';
				""")[0][0]
	print(counter)
	temp = frappe.db.get_all('Item', filters={'has_variants':1}, pluck='name',order_by='name')
	print(temp)
	for i in temp:
		variants = frappe.db.get_all('Item', filters={'variant_of':i, 'item_code':['not like', '%TCW-%']}, order_by='item_name', pluck='name')
		print(variants)
		for j in variants:
			counter += 1
			new_in = f"TCW-{'0'*(4-len(str(counter)))}{counter}"
			print(new_in)
			# doc = frappe.get_doc('Item', j)
			frappe.db.set_value('Item', j, 'item_code', new_in)
			# update_document_title('Item', doc.name, 'item_name', doc.item_name, doc.item_name, new_in)
			frappe.db.sql(f'''Update `tabSeries` set current={counter} where name="TCW-";''')
		frappe.db.commit()