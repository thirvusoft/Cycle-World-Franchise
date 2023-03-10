import frappe
import erpnext
import json
from frappe import _
from frappe.model.rename_doc import update_document_title
from erpnext.stock.doctype.item.item import (Item, update_variants, invalidate_cache_for_item)
from frappe.utils import strip, now
from cycle_world.cycle_world.custom.py.item_variant import make_variant_item_code
from frappe.model.naming import set_name_by_naming_series, make_autoname

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
			

@frappe.whitelist()
def update_item_price_from_purchase(items):
	if isinstance(items, str):
		items = json.loads(items)
	for i in items:
		if(i.get('item_code')):
			item = frappe.get_doc('Item', i.get('item_code'))
			item.update({
				'ts_margin':i.get('selling_margin') or 0,
				'mrp':i.get('mrp') or 0,
				'standard_buying_cost':i.get('rate'),
			})
			item.flags.ignore_permissions = True
			item.save()


def validate(doc, event=None):
	if(doc.variant_of and doc.attributes):
		for i in doc.attributes:
			i.update({
				'cw_name':frappe.db.get_value('CW Item Attribute', filters={'item_attribute':i.attribute, 'attribute_value':i.attribute_value}) or ''
			})
	if(doc.is_new()):
		autoname(doc, event)
		last_series = frappe.db.get_value('Item', {'has_variants':0, 'item_code':['like', '%TCW-%']}, 'item_code', order_by='`item_code` desc')
		if(last_series):
			counter = int(last_series.lower().split('tcw-')[-1])
			counter += 1
			new_series = f"TCW-{'0'*(4-len(str(counter)))}{counter}"
			doc.item_code = new_series
	
		return
	if(doc.opening_stock):
		doc.set_opening_stock()
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
	settings = frappe.get_single('Stock Settings')
	add_price(doc, 'standard_rate', settings.default_selling_pricelist or "Standard Selling")
	add_price(doc, 'standard_buying_cost', settings.default_buying_pricelist or "Standard Buying")
	add_price(doc, 'mrp', settings.default_mrp_pricelist or "MRP")

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
		elif(self.get(field)):
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
	if(doc.has_variants):
		doc.name = doc.brand_name if doc.item_group in ['BICYCLES', 'E-BIKES'] else doc.item_group 
	else:
		make_variant_item_code(template_ic, template_ic, doc, True)
		doc.name = doc.item_name

@frappe.whitelist()
def set_variant_name_for_manual_creation(doc):
	if isinstance(doc, str):
		doc = json.loads(doc)
		doc = frappe.get_doc(doc)
	if(not doc.get('variant_of')):
		return
	
	template_ic = doc.variant_of
	old_ic, old_in = doc.name, doc.item_name
	make_variant_item_code(template_ic, template_ic, doc, True)
	update_document_title('Item', old_ic, 'item_name', old_in, doc.item_name, doc.item_name, False)
	frappe.db.set_value('Item', doc.name, 'item_code', doc.item_code)
	frappe.db.set_value('Item', doc.name, 'item_name', doc.item_name)
	return doc.item_name


from frappe import scrub
from frappe.desk.reportview import get_filters_cond, get_match_cond
from frappe.utils import nowdate
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def item_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	doctype = "Item"
	conditions = []

	if isinstance(filters, str):
		filters = json.loads(filters)

	# Get searchfields from meta and use in Item Link field query
	meta = frappe.get_meta(doctype, cached=True)
	searchfields = meta.get_search_fields()

	# these are handled separately
	ignored_search_fields = ("item_name", "description")
	for ignored_field in ignored_search_fields:
		if ignored_field in searchfields:
			searchfields.remove(ignored_field)

	columns = ""
	extra_searchfields = [
		field
		for field in searchfields
		if not field in ["name", "item_group", "description", "item_name"]
	]

	if extra_searchfields:
		columns = ", " + ", ".join(extra_searchfields)

	searchfields = searchfields + [
		field
		for field in [searchfield or "name", "item_code", "item_group", "item_name"]
		if not field in searchfields
	]
	searchfields1  = searchfields
	searchfields2 = []
	# " or ".join([field + " like %(txt)s" for field in searchfields])
	splitted_txt = txt.split(" ")
	splitted_txt = [i for i in splitted_txt if(i)]
	if(not len(splitted_txt)):
		splitted_txt = ['']
	for field in searchfields:
		search_filters = []

		for i in splitted_txt:
			search_filters.append(field + f" like '{i.replace('%', '').replace('(', '').replace(')', '')}'")
		search_filters = " and ".join(search_filters)
		searchfields2.append(f"({search_filters})")
	searchfields2 = f"({' or '.join(searchfields2)})"
	b = []
	# searchfields = " or ".join([field + " like %(txt)s" for field in searchfields1])
	for field in searchfields1:
		a=[]
		for i in splitted_txt:
			a.append(field + f" like '%%{i.replace('%', '').replace('(', '').replace(')', '')}%%'")
		b.append(f'({" and ".join(a)})')

	searchfields = " or ".join(b)
	if filters and isinstance(filters, dict):
		if filters.get("customer") or filters.get("supplier"):
			party = filters.get("customer") or filters.get("supplier")
			item_rules_list = frappe.get_all(
				"Party Specific Item", filters={"party": party}, fields=["restrict_based_on", "based_on_value"]
			)

			filters_dict = {}
			for rule in item_rules_list:
				if rule["restrict_based_on"] == "Item":
					rule["restrict_based_on"] = "name"
				filters_dict[rule.restrict_based_on] = []

			for rule in item_rules_list:
				filters_dict[rule.restrict_based_on].append(rule.based_on_value)

			for filter in filters_dict:
				filters[scrub(filter)] = ["in", filters_dict[filter]]

			if filters.get("customer"):
				del filters["customer"]
			else:
				del filters["supplier"]
		else:
			filters.pop("customer", None)
			filters.pop("supplier", None)

	description_cond = ""
	if frappe.db.count(doctype, cache=True) < 50000:
		# scan description only if items are less than 50000
		description_cond = "or tabItem.description LIKE %(txt)s"
	return frappe.db.sql(
		"""select
			tabItem.name, tabItem.item_name
		from tabItem
		where tabItem.docstatus < 2
			and tabItem.disabled=0
			
			and (tabItem.end_of_life > %(today)s or ifnull(tabItem.end_of_life, '0000-00-00')='0000-00-00')
			and ({scond} or tabItem.item_code IN (select parent from `tabItem Barcode` where barcode LIKE %(txt)s)
				{description_cond})
			{fcond} {mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, item_name), locate(%(_txt)s, item_name), 99999),
			idx desc,
			name, item_name
		limit %(start)s, %(page_len)s """.format(
			columns=columns,
			scond=searchfields,
			fcond=get_filters_cond(doctype, filters, conditions).replace("%", "%%"),
			mcond=get_match_cond(doctype).replace("%", "%%"),
			description_cond=description_cond,
		),
		{
			"today": nowdate(),
			"txt": "%%%s%%" % txt.replace(' ', '%'),
			"_txt": txt.replace("%", ""),
			"start": start,
			"page_len": page_len,
		},
		as_dict=as_dict, debug=1
	)

def item_price_update(doc,action):
	
	for i in doc.items:
		if(i.get('item_code')):
			item = frappe.get_doc('Item', i.get('item_code'))
			purchase_items = frappe.get_doc(f"{i.receipt_document_type} Item",i.get('purchase_receipt_item'))
			item.update({
				'ts_margin':purchase_items.selling_margin or 0,
				'mrp':purchase_items.mrp or 0,
				'standard_buying_cost':purchase_items.rate or 0,
				'transportation_cost':i.get('applicable_charges') or 0
			})
			item.flags.ignore_permissions = True
			item.save()