import frappe
from erpnext.controllers.taxes_and_totals import get_itemised_tax_breakup_data
from cycle_world.cycle_world.custom.py.print_format import qrcode_as_png
from frappe.model.naming import make_autoname


def validate(doc, event):
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