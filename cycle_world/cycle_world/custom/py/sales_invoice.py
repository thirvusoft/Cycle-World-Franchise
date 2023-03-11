import frappe
from erpnext.controllers.taxes_and_totals import get_itemised_tax_breakup_data
from cycle_world.cycle_world.custom.py.print_format import qrcode_as_png
from frappe.model.naming import make_autoname

@frappe.whitelist()
def get_invoice_series_options():
    return frappe.get_meta('Sales Invoice').get_field('naming_series').options
def validate(doc, event):
    validate_selling_price_list(doc)
    set_qr_image(doc)
    itemised_tax, itemised_taxable_amount = get_itemised_tax_breakup_data(doc)
    tax_rates = {}
    originals = {}
    for i in itemised_tax:
        for j in itemised_tax[i]:
            if(not f"{j}{itemised_tax[i][j]['tax_rate']}" in tax_rates):
                originals[f"{j}{itemised_tax[i][j]['tax_rate']}"] = j
                tax_rates[f"{j}{itemised_tax[i][j]['tax_rate']}"] = [itemised_tax[i][j]['tax_rate'], itemised_tax[i][j]['tax_amount']]
            else:
                tax_rates[f"{j}{itemised_tax[i][j]['tax_rate']}"][1] += itemised_tax[i][j]['tax_amount']
    descriptions = []
    for i in tax_rates:
        desc = i
        if('sgst' in i.lower()):
            desc='SGST'
        elif('cgst' in i.lower()):
            desc='CGST'
        else:
            desc = originals[desc]
        descriptions.append({'description':desc, 'percent':tax_rates[i][0], 'tax_amount':tax_rates[i][1]})
    doc.update({
        'tax_table_print_format':descriptions
    })


def set_qr_image(doc):
    if(not doc.is_pos):
        return
    show_qr = frappe.db.get_value('POS Profile', doc.pos_profile, 'include_payment_qr_code_in_print')
    doc.show_qr = show_qr
    if(not show_qr):
        return
    upi_id = frappe.db.get_value('POS Profile', doc.pos_profile, 'upi_id')
    content = f"upi://pay?pa={upi_id}&pn={doc.company}&am={doc.rounded_total}&cu=INR&tn={doc.name}"
    file_url = qrcode_as_png(doc.name, content)
    doc.qr_code = file_url
    doc.upi_id = upi_id

def auto_name(self, event=None):
    if(self.sales_type=='Online Sales' and self.online_series):
        self.name = make_autoname(self.online_series, doc=self)
    elif(self.branch_series):
        self.name = make_autoname(self.branch_series, doc=self)

def validate_selling_price_list(doc):
    if frappe.db.get_single_value('Selling Settings', 'validate_selling_price_list'):
        price_list = frappe.db.get_single_value('Selling Settings', 'price_list')
        for i in doc.items:
            rate = frappe.db.get_value('Item Price', {'item_code':i.item_code}, 'price_list_rate', order_by = '`valid_from` desc')
            if(i.rate < rate):
                frappe.throw(
					f"""<b>Row #{i.idx}:</b> Selling rate ({i.rate}) for item <b>{i.item_code}</b> is lower than its {price_list} Price
                      should be atleast <b>{rate}</b>."""
				)