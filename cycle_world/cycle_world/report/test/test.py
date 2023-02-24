# # Copyright (c) 2023, Thirvusoft and contributors
# # For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = get_columns() or [], get_data() or []
# 	return columns,data


# def get_columns():
# 	columns = [
# 		{
# 			'fieldname':'item_group',
# 			'label':'Item Group',
# 			'fieldtype':'Data',
# 			'width':150
# 		},
# 		{
# 			'fieldname':'size',
# 			'label':'Size',
# 			'fieldtype':'Data',
# 			'width':100
# 		},
# 		{
# 			'fieldname':'brand',
# 			'label':'Brand',
# 			'fieldtype':'Data',
# 			'width':100
# 		},
# 		{
# 			'fieldname':'item',
# 			'label':'Item',
# 			'fieldtype':'Link',
# 			'width':300,
# 			'options':'Item'
# 		},
# 		{
# 			'fieldname':'standard_rate',
# 			'label':'Standard Selling',
# 			'fieldtype':'Currency',
# 			'width':100,
# 		},
  	
  
# 		{
# 			'fieldname':'mrp',
# 			'label':'MRP',
# 			'fieldtype':'Currency',
# 			'width':100,
# 		},
 
# 	]
# 	return columns

# def get_data():
# 	data = []
# 	item_group = frappe.db.get_all('Item Group', filters={'parent_item_group':'All Item Groups', 'is_group':1}, pluck='name')
# 	for ig in item_group:
# 		if(ig != 'BICYCLES'):
# 			data.append({'item_group':ig, 'indent':0, 'is_bold':1})
# 			sub_groups = get_all_sub_group(ig)
# 			items = frappe.db.get_all('Item', filters={'item_group':['in', sub_groups]}, fields=['name as item', 'standard_rate', 'mrp','ts_margin as margin',"ts_discount_ as discount","transportation_cost as ts_cost","shipping_cost as lab_cost"])
# 			for i in items:
# 				i['indent']=1
# 			data.extend(items)
# 		else:
# 			data.append({'item_group':ig, 'indent':0, 'is_bold':1})
# 			brands = frappe.db.get_all('Brand', pluck='name', order_by='name')
# 			print(brands)
# 			sizes = frappe.db.get_all('Item Attribute Value', filters={'parent':'WHEEL SIZE'}, pluck='attribute_value', order_by='name')
# 			for size in sizes:
# 				data.append({'size':size, 'indent':1, 'is_bold':1})
# 				for brand in brands:
# 					data.append({'brand':brand, 'indent':2, 'is_bold':1})
# 					branded_items = frappe.db.get_all('Item', filters={'brand_name':brand, 'has_variants':0}, pluck='name')
# 					sized_items = frappe.db.get_all('Item Variant Attribute', filters={'attribute':'WHEEL SIZE', 'attribute_value':size, 'parent':['in', branded_items]}, pluck='parent')
     
# 				items = frappe.db.get_all('Item', filters={'name':['in', sized_items]}, fields=['name as item', 'standard_rate', 'mrp','ts_margin as margin'])
# 				for i in items:
# 					i['indent']=5
# 				# print("efbbbbbbbbbbbbbbbbbb")
# 				data.extend(items)

# 	# data.append(item_group)
# 	return data



# def get_all_sub_group(parent_group):
# 	sub_groups = []
# 	parents = [parent_group]
# 	for i in parents:
# 		# frappe.errprint(i)
# 		curr_parents = frappe.db.get_all('Item Group', filters={'parent_item_group':i, 'is_group':1}, pluck='name')
# 		sub_groups.extend(frappe.db.get_all('Item Group', filters={'parent_item_group':i, 'is_group':0}, pluck='name'))
# 		parents.extend(curr_parents)
# 	return sub_groups


import frappe



def execute(filters=None):
    columns = [
        {
            "label": ("Item Group"),
            "fieldname": "item_group",
            "fieldtype": "Data",
            "width": 300
        },
        {
            "label": ("Available Stock"),
            "fieldname": "item",
            "fieldtype": "Data",
            "width": 300
        },
         {
            "label": ("Standard Buying Cost"),
            "fieldname": "st_buying_cost",
            "fieldtype": "Data",
            "width": 300
        },
          {
            "label": ("MRP"),
            "fieldname": "mrp",
            "fieldtype": "Data",
            "width": 300
        },
      
    ]
    
    data = []
    check=2
    item_groups = frappe.get_all('Item Group', filters={'parent_item_group':'All Item Groups', 'is_group':1}, fields=['name'])
    for item_group in item_groups:
        print(item_group["name"])
        if item_group["name"] != 'BICYCLES':
            item_group_row = {
                "item_group": item_group.name,
                    "indent" : 0,
                    "is_bold":1
                
            }
            data.append(item_group_row)
            
            
            parents = [item_group.name]
            for i in parents:
            
                curr_parents = frappe.db.get_all('Item Group', filters={'parent_item_group':i, 'is_group':1}, pluck='name')
                sub = frappe.db.get_all('Item Group', filters={'parent_item_group':i, 'is_group':0}, pluck='name')
                
                
                
            if curr_parents:
                
                for j in curr_parents:
                    
                    item_group_row = {
                "item_group": j,
                    "indent" : 1
                
                }
                    data.append(item_group_row)
                    
                    
                            
                    sub1=frappe.db.get_all('Item Group', filters={'parent_item_group':j, 'is_group':0}, pluck='name')
                    sub2=frappe.db.get_all('Item Group', filters={'parent_item_group':j, 'is_group':1}, pluck='name')
                    if sub1:
                        
                        for k in sub1:
                            items = frappe.db.get_all('Item', filters={'item_group':k}, fields=['name as item', 'standard_rate', 'mrp',])
                         
                            item_group_row = {
                        "item_group": k,
                        "indent" : 1
                    
                        }
                            data.append(item_group_row)
                            for v in items:
                               
                                item_group_row = {
                                "item_group": v["item"],
                                "item":"",
                                "st_buying_cost":v["standard_rate"],
                                "mrp":v["mrp"],
                                
                                "indent" : 2
                            
                                }
                                data.append(item_group_row)
                    if sub2:
                            for l in sub2:
                                item_group_row = {
                            "item_group": l,
                            "indent" : 2
                        
                            }
                                data.append(item_group_row)
                                sub3=frappe.db.get_all('Item Group', filters={'parent_item_group':l, 'is_group':0}, pluck='name')
                            
            
                
                                if sub3:
                                    for m in sub3:
                                        item_group_row = {
                                    "item_group": m,
                                    "indent" : 3
                                
                                    }
                                        data.append(item_group_row)
                                        
                                    
                        
                        
            if sub:
                    for j in sub:
                        items = frappe.db.get_all('Item', filters={'item_group':j}, fields=['name as item', 'standard_rate', 'mrp',])
                        item_group_row = {
                    "item_group": j,
                    
                        "indent" : 1}
                        data.append(item_group_row)
                        for v in items:
                            item_group_row = {
                        "item_group": v["item"],
                        "item":"",
                        "st_buying_cost":v["standard_rate"],
                        "mrp":v["mrp"],
                        
                        "indent" : 2
                    
                        }
                            data.append(item_group_row)
                            
                    
            else:
                # if this is a child item group
                
                item_group_row['indent'] = 0
                # data.append(item_group_row)
        else:
            if filters.get('filter') == "Brand":
                check=0
            if filters.get('filter') == "Size":
                check=1
            item_group_row = {
                "item_group": item_group.name,
                    "indent" : 0
                
            }
            data.append(item_group_row)
            
            if check==0:
                brands = frappe.db.get_all('Brand', pluck='name', order_by='name')
                for brand in brands:
                    # data.append({'brand':brand, 'indent':2, 'is_bold':1})
                    branded_items = frappe.db.get_all('Item', filters={'brand_name':brand, 'has_variants':0}, pluck='name')
                    # for i in branded_items:
                    items = frappe.db.get_all('Item', filters={'brand_name':brand, 'has_variants':0}, fields=['name as item', 'standard_rate','mrp'])
                    for v in items:
                        item_group_row = {
                    "item_group": v["item"],
                    "item":"",
                    "st_buying_cost":v["standard_rate"],
                    "mrp":v["mrp"],
                    
                    "indent" : 1
                
                    }
                        data.append(item_group_row)
            if check==1:
                sizes = frappe.db.get_all('Item Attribute Value', filters={'parent':'WHEEL SIZE'}, pluck='attribute_value', order_by='name')
                for size in sizes:
                    sized_items = frappe.db.get_all('Item Variant Attribute', filters={'attribute':'WHEEL SIZE', 'attribute_value':size, }, pluck='parent')
                    for v in sized_items:
                        items = frappe.db.get_all('Item', filters={'name': v}, fields=['name as item', 'standard_rate', 'mrp'])
                        for j in items:
                            item_group_row = {
                        "item_group": j["item"],
                        "item":"",
                        "st_buying_cost":j["standard_rate"],
                        "mrp":j["mrp"],
                        
                        "indent" : 1
                    
                        }
                            data.append(item_group_row)
                                
                        
       
    
    return columns, data