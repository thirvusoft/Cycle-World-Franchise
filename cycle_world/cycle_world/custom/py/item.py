import frappe
import erpnext
import json
from frappe import _
from frappe.model.rename_doc import update_document_title
from erpnext.stock.doctype.item.item import (Item, update_variants, invalidate_cache_for_item)
from frappe.utils import strip, now
from cycle_world.cycle_world.custom.py.item_variant import make_variant_item_code
from frappe.model.naming import set_name_by_naming_series

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

	def after_rename(self, old_name, new_name, merge):
		if merge:
			self.validate_duplicate_item_in_stock_reconciliation(old_name, new_name)
			frappe.msgprint(
				_("It can take upto few hours for accurate stock values to be visible after merging items."),
				indicator="orange",
				title="Note",
			)

		if self.published_in_website:
			invalidate_cache_for_item(self)

		# frappe.db.set_value("Item", new_name, "item_code", new_name)

		if merge:
			self.set_last_purchase_rate(new_name)
			self.recalculate_bin_qty(new_name)

		for dt in ("Sales Taxes and Charges", "Purchase Taxes and Charges"):
			for d in frappe.db.sql(
				"""select name, item_wise_tax_detail from `tab{0}`
					where ifnull(item_wise_tax_detail, '') != ''""".format(
					dt
				),
				as_dict=1,
			):

				item_wise_tax_detail = json.loads(d.item_wise_tax_detail)
				if isinstance(item_wise_tax_detail, dict) and old_name in item_wise_tax_detail:
					item_wise_tax_detail[new_name] = item_wise_tax_detail[old_name]
					item_wise_tax_detail.pop(old_name)

					frappe.db.set_value(
						dt, d.name, "item_wise_tax_detail", json.dumps(item_wise_tax_detail), update_modified=False
					)

	def autoname(self):
		if frappe.db.get_default("item_naming_by") == "Naming Series":
			if(self.has_variants):
				self.name = self.item_code or self.brand or self.item_name
				self.item_code = self.item_code or self.brand or self.item_name
				self.item_name = self.item_name or self.brand or self.item_code
			else:
				set_name_by_naming_series(self)
		else:
			if self.variant_of:
				if not self.item_code:
					template_item_name = frappe.db.get_value("Item", self.variant_of, "item_name")
					make_variant_item_code(self.variant_of, template_item_name, self)
			else:
				self.name = self.item_code
			

			


def validate(doc, event=None):
	if(doc.variant_of and doc.attributes):
		for i in doc.attributes:
			i.update({
				'cw_name':frappe.db.get_value('CW Item Attribute', filters={'item_attribute':i.attribute, 'attribute_value':i.attribute_value}) or ''
			})
	if(doc.is_new()):
		autoname(doc, event)
		return
	if(doc.get('dont_save') or not frappe.db.exists('Item', doc.name)):return
	doc.additional_cost = (doc.get('transportation_cost') or 0) + (doc.get('shipping_cost') or 0) + (doc.get('other_costs') or 0)
	doc.standard_rate = float(doc.get('standard_buying_cost') or 0) + (
						doc.get('additional_cost') or 0)
	doc.standard_rate = doc.get('standard_rate') + doc.get('standard_rate')*(doc.get('ts_margin') or 0)/100 
	doc.standard_rate = doc.get('standard_rate') - doc.get('standard_rate')*(doc.get('ts_discount_') or 0)/100 
	if(doc.get('mrp') and (doc.get('mrp') or 0) < (doc.get('standard_rate') or 0)):
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
		ip = frappe.get_all('Item Price', {'price_list':price_list, 'item_code':self.name, 'valid_upto':["is","not set"]}, 'name')
		print(('Item Price', {'price_list':price_list, 'item_code':self.name, 'valid_upto':["is","not set"]}, 'name'))
		if(ip):
			exists_doc = frappe.get_doc('Item Price', ip[0].name)
			if(not self.get(field) or self.get('has_variants')):return
			if exists_doc.price_list_rate == self.get(field):
				return
			else:
				exists_doc.valid_upto = now()
				exists_doc.save()
		
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
		else:
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
def autoname(doc, event):
	template_ic = doc.variant_of
	make_variant_item_code(template_ic, template_ic, doc, True)

@frappe.whitelist()
def set_variant_name_for_manual_creation(doc):
	if isinstance(doc, str):
		doc = json.loads(doc)
		doc = frappe.get_doc(doc)
	if(not doc.get('variant_of')):
		return
	
	template_ic = doc.variant_of
	old_ic, old_in = doc.item_code, doc.item_name
	make_variant_item_code(template_ic, template_ic, doc, True)
	# update_document_title('Item', old_ic, 'item_name', old_in, doc.item_name, doc.item_code, False)
	frappe.db.set_value('Item', doc.name, 'item_code', doc.item_code)
	frappe.db.set_value('Item', doc.name, 'item_name', doc.item_name)
	return doc.item_code

