// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["test"] = {
	"filters": [

	],
	"formatter":function(value, row, column, data, default_formatter) {
		// console.log(value, row, column, data, default_formatter)
		return default_formatter(value, row, column, data)
	},"tree":true
};
