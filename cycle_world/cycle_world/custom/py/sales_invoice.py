import frappe
from erpnext.controllers.taxes_and_totals import get_itemised_tax_breakup_data
from cycle_world.cycle_world.custom.py.print_format import qrcode_as_png
def validate(doc, event):
    set_qr_image(doc)
    itemised_tax, itemised_taxable_amount = get_itemised_tax_breakup_data(doc)
    descriptions = []
    final_taxes = {}
    for i in itemised_tax:
        taxes = list(itemised_tax[i].keys())
        tax_rate = list(itemised_tax[i].values())[0]['tax_rate']
        taxes = replace_in_list(taxes, 'Output Tax')
        taxes = replace_in_list(taxes, 'Input Tax')
        taxes = split_in_list(taxes, '@')
        tax_list = [i+f' @ {tax_rate}' for i in taxes]
        descriptions+=taxes
        final_taxes = add_to_tax_list(final_taxes, tax_list, itemised_tax[i])
    descriptions = list(set(descriptions))
    doc.update({
        'tax_table_print_format':list(final_taxes.values())
    })

def replace_in_list(lst, from_word='', to_word=''):
    new_lst = []
    for i in lst:
        new_lst.append(i.replace(from_word, to_word).strip())
    return new_lst

def split_in_list(lst, separator='', max_split=-1):
    new_lst = []
    for i in lst:
        new_lst.append(i.split(separator, max_split)[0].strip())
    return new_lst

def add_to_tax_list(taxes, tax_list, curr_tax):
    for key in tax_list:
        row1=list(curr_tax.values())[0]
        if(row1['tax_rate'] == 0):continue
        if(key not in taxes):
            lst = {'description':key, 'percent':row1['tax_rate'], 'tax_amount':row1['tax_amount']}
            taxes[key] = lst
        else:
            lst = taxes[key]
            lst['tax_amount'] += row1['tax_amount']
    return taxes

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

