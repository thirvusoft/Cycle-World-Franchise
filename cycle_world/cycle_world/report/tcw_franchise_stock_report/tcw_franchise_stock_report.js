// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["TCW Franchise Stock Report"] = {
	"filters": [

	]
};
// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["TCW Franchise Stock Report"] = {
	"filters": [
		// {
		// "fieldname":"filter",
		// "label": ("Select Brand or Size"),
		// "fieldtype": "Select",
		// "options": "\nBrand\nSize",
		// // "default": "Completed"
		// },
		
		{
			"fieldname":"hierarchy",
			"label": ("BICYCLE HIERARCHY"),
			"fieldtype": "Select",
			"options": "\nWHEEL SIZE\nBrand",
			"reqd": 1,
			"default": "WHEEL SIZE"
			},
		{
			"fieldname":"warehouse",
			"label": ("Select Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"reqd": 1,
			"default": frappe.defaults.get_user_permissions()['Warehouse']?frappe.defaults.get_user_permissions()['Warehouse'][0].doc:''
			}
	],
	"initial_depth":0,
	"formatter":function(value, row, column, data, default_formatter) {
		// console.log(value, row, column, data, default_formatter)
		return default_formatter(value, row, column, data)
	}
};
