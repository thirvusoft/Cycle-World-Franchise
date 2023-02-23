# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

BICYCLE_HIERARCHY = {'Brand', 'WHEEL SIZE'}

def execute(filters=None):
	columns, data = get_columns() or [], get_data() or []
	return columns, data



def get_columns():
	columns = [
		{
			'fieldname':'item_group',
			'label':'Item Group',
			'fieldtype':'Data',
			'width':150
		},
		{
			'fieldname':'size',
			'label':'Size',
			'fieldtype':'Data',
			'width':100
		},
		{
			'fieldname':'brand',
			'label':'Brand',
			'fieldtype':'Data',
			'width':100
		},
		{
			'fieldname':'item',
			'label':'Item',
			'fieldtype':'Link',
			'width':300,
			'options':'Item'
		},
		{
			'fieldname':'standard_rate',
			'label':'Standard Selling',
			'fieldtype':'Currency',
			'width':100,
		},
		{
			'fieldname':'mrp',
			'label':'MRP',
			'fieldtype':'Currency',
			'width':100,
		},
  {
			'fieldname':'margin',
			'label':'Margin',
			'fieldtype':'Currency',
			'width':100,
		},
  {
			'fieldname':'discount',
			'label':'Discount',
			'fieldtype':'Currency',
			'width':100,
		},
	]
	return columns
def get_data():
	data = []
	item_group = get_all_item_group()
	tot_bic = []
	for ig in item_group:
		if(ig != 'BICYCLES'):
			data.append({'item_group':ig, 'indent':0, 'is_bold':1})
			sub_groups = get_all_sub_group(ig)
			print(sub_groups)
			# frappe.errprint(sub_groups)
			items = frappe.db.get_all('Item', filters={'item_group':['in', sub_groups]}, fields=['name as item', 'standard_rate', 'mrp',])
			for i in items:
				i['indent']=1
			data.extend(items)
		else:
			data.append({'item_group':ig, 'indent':0, 'is_bold':1})
			brands = frappe.db.get_all('Brand', pluck='name', order_by='name')
			sizes = frappe.db.get_all('Item Attribute Value', filters={'parent':'WHEEL SIZE'}, pluck='attribute_value', order_by='name')
			for size in sizes:
				data.append({'size':size, 'indent':1, 'is_bold':1})
				for brand in brands:
					data.append({'brand':brand, 'indent':2, 'is_bold':1})
					branded_items = frappe.db.get_all('Item', filters={'brand_name':brand, 'has_variants':0}, pluck='name')
					# branded_items = frappe.db.sql(f"""
					# 				SELECT name 
					# 				FROM `tabItem`
					# 				WHERE brand_name='{brand}' and 
					# 					  has_variants = 0
					# """, as_list=1)
					# branded_items=[j for i in branded_items for j in i]
					# print(branded_items, brand)
					# frappe.errprint(branded_items)
					sized_items = frappe.db.get_all('Item Variant Attribute', filters={'attribute':'WHEEL SIZE', 'attribute_value':size, 'parent':['in', branded_items]}, pluck='parent')
					# cond = ''
					# if(len(branded_items) == 1):
					# 	cond = f" and att.parent = '{branded_items[0]}'"
					# elif(len(branded_items)>1):
					# 	cond = f" and att.parent in {tuple(branded_items)}"
					# items = frappe.db.sql(f"""
					# 				SELECT it.name as item, it.standard_rate, it.mrp
					# 				FROM `tabItem` it
					# 				LEFT JOIN
					# 				`tabItem Variant Attribute` att ON att.parent=it.name
					# 				WHERE att.attribute = "WHEEL SIZE" and att.attribute_value = "{size}" {cond}

					# """, as_dict = 1)
					# tot_bic += items
					# frappe.errprint(len(tot_bic))
					items = frappe.db.get_all('Item', filters={'name':['in', sized_items]}, fields=['name as item', 'standard_rate', 'mrp','ts_margin'])
					for i in items:
						print(i)
						i['indent']=4
					data.extend(items)

	# frappe.errprint(len(tot_bic))	
	# frappe.errprint(tot_bic)
	# frappe.errprint(len(list(set(tot_bic))))
	return data

def get_all_item_group():
	group = frappe.db.get_all('Item Group', filters={'parent_item_group':'All Item Groups', 'is_group':1}, pluck='name')
	return group

def get_all_sub_group(parent_group):
	sub_groups = []
	parents = [parent_group]
	for i in parents:
		# frappe.errprint(i)
		curr_parents = frappe.db.get_all('Item Group', filters={'parent_item_group':i, 'is_group':1}, pluck='name')
		sub_groups.extend(frappe.db.get_all('Item Group', filters={'parent_item_group':i, 'is_group':0}, pluck='name'))
		parents.extend(curr_parents)
	return sub_groups