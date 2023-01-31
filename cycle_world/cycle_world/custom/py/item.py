import frappe
import erpnext
from frappe import _
from erpnext.stock.doctype.item.item import (Item, update_variants)

class CycleWorldItem(Item):
	def update_variants(self):
		if self.flags.dont_update_variants or frappe.db.get_single_value(
			"Item Variant Settings", "do_not_update_variants"
		):
			return
		if self.has_variants:
			variants = frappe.db.get_all("Item", fields=["item_code"], filters={"variant_of": self.name})
			if variants:
				if len(variants) <= 5:
					update_variants(variants, self, publish_progress=False)
					frappe.msgprint(_("Item Variants updated"))
				else:
					frappe.enqueue(
						"erpnext.stock.doctype.item.item.update_variants",
						variants=variants,
						template=self,
						now=frappe.flags.in_test,
						timeout=600,
					)
def validate(doc, event):
	
	if not doc.barcodes:
		doc.append('barcodes',
					{
						"barcode":doc.item_code
					}
	)
	else:
		for i in doc.barcodes:
			if (i.barcode!=doc.item_code):
				doc.append('barcodes',
					{
						"barcode":doc.item_code
					}
				)
	
	if(doc.variant_of):
		set_variant_name_for_manual_creation(doc)
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


@frappe.whitelist()
def get_attributes(template=None):
	return frappe.db.get_all('Item Variant Attribute', filters={'parent':template, 'parentfield':'attributes'}, pluck='attribute', order_by='idx')

@frappe.whitelist()
def get_link_options(doctype, txt, searchfield, start, page_len, filters):
	# frappe.errprint(args)
	doctype = 'Item Attribute Value'
	name_field='attribute_value'
	print(doctype, txt, searchfield, start, page_len, filters)
	searchfields = ['name', 'attribute_value', 'abbr']
	fields = ', '.join(searchfields)
	scond = " or ".join(field + f" like '%{txt}%'" for field in searchfields)
	scond = f'({scond})' + f' and parent ="{filters["attribute"]}"'
	return frappe.db.sql(
		f"""select {fields} from `tab{doctype}`
		where 
			{scond}
		order by
			idx
		limit {start}, {page_len}"""
	)


def set_variant_name_for_manual_creation(doc):
	from cycle_world.cycle_world.custom.py.item_variant import make_variant_item_code
	template_ic = doc.variant_of
	make_variant_item_code(template_ic, template_ic, doc, True)

