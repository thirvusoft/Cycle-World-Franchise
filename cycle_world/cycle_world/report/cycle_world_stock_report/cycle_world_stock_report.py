import frappe



def execute(filters=None):
  
    columns = [
        {
    
            "label": ("Item Group"),
            "fieldname": "item_group",
            "fieldtype": "Data",
            "width": 500
        },
        {
            "label": ("Available Stock"),
            "fieldname": "available_stock",
            "fieldtype": "Data",
            "width": 150
        },
         {
            "label": ("Standard Buying Cost"),
            "fieldname": "st_buying_cost",
            "fieldtype": "Data",
            "width": 150
        },
          {
            "label": ("MRP"),
            "fieldname": "mrp",
            "fieldtype": "Data",
            "width": 150
        },
      
    ]
    
    data = []
    check=2
    if filters.get("warehouse"):
        warehouse_filter=filters.get("warehouse")
		
    item_groups = frappe.get_all('Item Group', filters={'parent_item_group':'All Item Groups', 'is_group':1}, fields=['name'])
    # item_groups = frappe._dict()
    # item_groups['name'] = 'BICYCLES'
    for item_group in item_groups:
        
        if item_group["name"] != 'BICYCLES':
            item_group_row = {
                "item_group": f"""<b>{item_group.name}</b>""",
                    "indent" : 0,
                   
                
            }
            data.append(item_group_row)
            
            
            parents = [item_group.name]
            for i in parents:
            
                curr_parents = frappe.db.get_all('Item Group', filters={'parent_item_group':i, 'is_group':1}, pluck='name')
                sub = frappe.db.get_all('Item Group', filters={'parent_item_group':i, 'is_group':0}, pluck='name')
                
                
                
            if curr_parents:
                
                for j in curr_parents:
    #                 frappe.db.sql(
	# 	"""select sum(opening_stock) from `tabItem`
	# 	where item_code = %s 
	# 	limit 1""",
	# 	(j),
	# as_dict=1
	# )
                    item_group_row = {
                "item_group": f"""<b>{j}</b>""",
                    "indent" : 1
                
                }
                    data.append(item_group_row)
                    
                    
                            
                    sub1=frappe.db.get_all('Item Group', filters={'parent_item_group':j, 'is_group':0}, pluck='name',order_by="name asc")
                    sub2=frappe.db.get_all('Item Group', filters={'parent_item_group':j, 'is_group':1}, pluck='name',order_by="name asc")
                    if sub1:
                        
                        for k in sub1:
                       
                            items = frappe.db.get_all('Item', filters={'item_group':k}, fields=['name as item', 'standard_rate', 'mrp',])
                         
                            item_group_row = {
                        "item_group": f"""<b>{k}</b>""",
                        "indent" : 2
                    
                        }
                            data.append(item_group_row)
                            for v in items:
                                bin_list=frappe.db.sql(
		"""select actual_qty from `tabBin`
		where item_code = %s and warehouse = %s
		limit 1""",
		( v["item"], filters.get("warehouse")),
	as_dict=1
	)
                              
                                if bin_list:
                                    item_group_row = {
                                    "item_group": v["item"],
                                    "item":"",
                                    "available_stock":bin_list[0]["actual_qty"],
                                    "st_buying_cost":v["standard_rate"],
                                    "mrp":v["mrp"],
                                    
                                    "indent" : 3
                                
                                    }
                                    data.append(item_group_row)
                                else:
                                    item_group_row = {
                                    "item_group": v["item"],
                                    "item":"",
                                    "available_stock":"",
                                    "st_buying_cost":v["standard_rate"],
                                    "mrp":v["mrp"],
                                    
                                    "indent" : 3
                                
                                    }
                                    data.append(item_group_row)
                                    
                    if sub2:
                            for l in sub2:
                                item_group_row = {
                            "item_group": f"""<b>{l}</b>""",
                            "indent" : 2
                        
                            }
                                data.append(item_group_row)
                                sub3=frappe.db.get_all('Item Group', filters={'parent_item_group':l, 'is_group':0}, pluck='name', order_by="name asc")
                                print("sub")
                                print(sub3)
            
                
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
                    "item_group": f"""<b>{j}</b>""",
                    
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
            if filters.get("hierarchy") == "Brand":
                check=0
            if filters.get("hierarchy") == "WHEEL SIZE":
                check=1
            item_group_row = {
               "item_group": f"""<b>{item_group.name}</b>""",
                    "indent" : 0
                
            }
            data.append(item_group_row)
            
            if check==0:
                brands = frappe.db.get_all('Brand', pluck='name', order_by='name asc')
                for brand in brands:
                    # data.append({'brand':brand, 'indent':2, 'is_bold':1})
                    branded_items = frappe.db.get_all('Item', filters={'brand_name':brand, 'has_variants':0}, pluck='name')
                    # for i in branded_items:
                    items = frappe.db.get_all('Item', filters={'brand_name':brand, 'has_variants':0}, fields=['name as item', 'standard_rate','mrp'])
                    item_group_row = {
                    "item_group": brand,
                    "item":"",
                    "st_buying_cost":"",
                    "mrp":"",
                    
                    "indent" : 1
                
                    }
                    data.append(item_group_row)
                    for v in items:
                        bin_list=frappe.db.sql(
		"""select actual_qty from `tabBin`
		where item_code = %s and warehouse = %s
		limit 1""",
		( v["item"],filters.get("warehouse")),
	as_dict=1
	)
                        if bin_list:
                            item_group_row = {
                            "item_group": v["item"],
                            "item":"",
                            "available_stock":bin_list[0]["actual_qty"],
                            "st_buying_cost":v["standard_rate"],
                            "mrp":v["mrp"],
                            
                            "indent" : 2
                        
                            }
                            data.append(item_group_row)
                        else:
                            item_group_row = {
                            "item_group": v["item"],
                            "item":"",
                            "available_stock":"",
                            "st_buying_cost":v["standard_rate"],
                            "mrp":v["mrp"],
                            
                            "indent" : 2
                        
                            }
                            data.append(item_group_row)
                            
            if check==1:
                sizes = frappe.db.get_all('Item Attribute Value', filters={'parent':filters.get("hierarchy")}, pluck='attribute_value', order_by='attribute_value')
                for size in sizes:
                    item_group_row = {
                        "item_group":f"""<b>{size}</b>""",
                        "item":"",
                        "st_buying_cost":"",
                        "mrp":"",
                        
                        "indent" : 1
                    
                        }
                    data.append(item_group_row)
                    
                    sized_items = frappe.db.get_all('Item Variant Attribute', filters={'attribute':filters.get("hierarchy"), 'attribute_value':size, }, pluck='parent')
                    for v in sized_items:
                        items = frappe.db.get_all('Item', filters={'name': v}, fields=['name as item', 'standard_rate', 'mrp'])
                        for j in items:
                            bin_list=frappe.db.sql(
		"""select actual_qty from `tabBin`
		where item_code = %s and warehouse = %s
		limit 1""",
		( j["item"], filters.get("warehouse")),
	as_dict=1
	)
                            if bin_list:
                                
                                item_group_row = {
                            "item_group": j["item"],
                            "item":"",
                            "available_stock":bin_list[0]["actual_qty"],
                            "st_buying_cost":j["standard_rate"],
                            "mrp":j["mrp"],
                            
                            "indent" : 2
                        
                            }
                                data.append(item_group_row)
                            else:
                                item_group_row = {
                            "item_group": j["item"],
                            "item":"",
                            "available_stock":"",
                            "st_buying_cost":j["standard_rate"],
                            "mrp":j["mrp"],
                            
                            "indent" : 2
                        
                            }
                                data.append(item_group_row)
                                
                                
                        
    for i in range(2,-1,-1):
        print(i)
        index=0
        sum=None
        
        for j in range(len(data)):
            if data[j]["indent"]==i:
                
                index=j 
                frappe.errprint(f"{index}-index-{i}-i")
                # sum=0
                
                for k in range(j+1,len(data)):
                    if(i==1):
                        frappe.errprint(data[k]["indent"])
                    if data[k]["indent"]==i+1:
                        sum= (sum or 0) + (data[k].get("available_stock") or 0)
                        if(i==1):
                            frappe.errprint(f'{data[k]["indent"]}-{j+1}-{index}-{sum}-i-{i}')
                        
                       
                       
                    elif(data[k]["indent"]==i):
                        if(sum):
                            data[index]["available_stock"]=sum
                        
                        print(index,sum)
                        sum=None
                        if(i==1):
                            frappe.errprint("-----------------------")
                        break
                        
                        
                        
            
            
        
    
    return columns, data