import frappe
import erpnext
from frappe import _



def validate(doc, event=None):
	if(doc.get('dont_save')):return
	doc.additional_cost = (doc.get('transportation_cost') or 0) + (doc.get('shipping_cost') or 0) + (doc.get('other_costs') or 0)
	doc.standard_rate = (doc.get('standard_buying_cost') or 0) + (
						doc.get('additional_cost') or 0)
	doc.standard_rate = doc.get('standard_rate') + doc.get('standard_rate')*(doc.get('ts_margin') or 0)/100 
	doc.standard_rate = doc.get('standard_rate') - doc.get('standard_rate')*(doc.get('ts_discount_') or 0)/100 
	if((doc.get('mrp') or 0) < (doc.get('standard_rate') or 0)):
		frappe.msgprint(f'Standard Selling rate({doc.get("standard_rate")}) is greater than MRP rate({doc.get("mrp")}).')
	insert_prices(doc)
	
def insert_prices(doc):
	add_price(doc, 'standard_rate', 'Standard Selling')
	add_price(doc, 'standard_buying_cost', 'Standard Buying')
	add_price(doc, 'mrp', 'MRP')

def add_price(self, field=None, price_list=None):
	"""Add a new price"""
	if(not field):
		return
	
	if not price_list:
		price_list = frappe.db.get_single_value(
			"Selling Settings", "selling_price_list"
		) or frappe.db.get_value("Price List", _("Standard Selling"))
	if price_list:
		ip = frappe.get_value('Item Price', {'price_list':price_list, 'item_code':self.name})
		if(ip):
			frappe.delete_doc_if_exists('Item Price', ip, force=1)
		if(not self.get(field) or self.get('has_variants')):return
		item_price = frappe.get_doc(
			{
				"doctype": "Item Price",
				"price_list": price_list,
				"item_code": self.name,
				"uom": self.stock_uom,
				"brand": self.brand,
				"currency": erpnext.get_default_currency(),
				"price_list_rate": self.get(field) or 0,
			}
		)
		item_price.save()
