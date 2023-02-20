import frappe
from frappe.utils import get_link_to_form
import json

def create_landed_voucher(doc, event = None):
    """on_submit Event"""
    # frappe.db.commit()
    if isinstance(doc, str):
        doc = json.loads(doc)
        doc = frappe.get_doc(doc)
    if(doc.doctype=='Purchase Invoice'):
        if(doc.update_stock != 1):
            return
    purchase_doc = frappe.get_doc(doc.doctype, doc.name)
    fixed_expense = get_fixed_additional_costs(purchase_doc)
    if(len(purchase_doc.landed_cost_taxes)==0 and len(fixed_expense)==0):
        return
   
    
    lnd_doc = frappe.new_doc('Landed Cost Voucher')
    purchase_receipts = [
        {
            'receipt_document_type':purchase_doc.doctype,
            'receipt_document':purchase_doc.name,
            'supplier':purchase_doc.supplier,
            'posting_date':purchase_doc.posting_date,
            'grand_total':purchase_doc.grand_total,
        }
    ]
    lnd_doc.update({
        'distribute_charges_based_on':purchase_doc.distribute_charges_based_on,
        'purchase_receipts':purchase_receipts,
        'taxes': (purchase_doc.landed_cost_taxes or []) +fixed_expense
    })
    lnd_doc.save()
    lnd_doc.submit()

def get_fixed_additional_costs(purchase_doc):
    exp_acc = ''
    if(len(purchase_doc.landed_cost_taxes)==0):
        exp_acc = frappe.db.get_value('Company', purchase_doc.company, 'default_landed_cost_account')
        if(not exp_acc):
            abbr = frappe.db.get_value('Company', purchase_doc.company, 'abbr')
            if(frappe.db.exists('Account', f"Freight and Forwarding Charges - {abbr}")):
                exp_acc = f"Freight and Forwarding Charges - {abbr}"
            else:
                frappe.throw(f'''Please fill <b>Default Landed Cost Voucher Account</b> under 
                <b>Accounts Settings</b> section in {get_link_to_form("Company", purchase_doc.company)}''')
    else:
        exp_acc = purchase_doc.landed_cost_taxes[0].get('expense_account')
    expense = []
    for i in purchase_doc.items:
        expense.append({
            'expense_account':exp_acc,
            'exchange_rate':1,
            'description':f'Labour Costs + Other Costs for Item <b>{i.item_code}</b>. This cost is fetched from this Item',
            'amount':(frappe.db.get_value('Item', i.item_code, 'shipping_cost') or 0) + (frappe.db.get_value('Item', i.item_code, 'other_costs') or 0),
            'base_amount':(frappe.db.get_value('Item', i.item_code, 'shipping_cost') or 0) + (frappe.db.get_value('Item', i.item_code, 'other_costs') or 0)
        })
    return expense
def on_cancel(doc, event=None):
    lcv = frappe.db.get_all('Landed Cost Purchase Receipt', filters={'receipt_document_type':doc.doctype, 'receipt_document':doc.name, 'docstatus':1}, pluck='parent')
    for i in list(set(lcv)):
        lnd = frappe.get_doc('Landed Cost Voucher', i)
        lnd.cancel()

def on_trash(doc, event=None):
    lcv = frappe.db.get_all('Landed Cost Purchase Receipt', filters={'receipt_document_type':doc.doctype, 'receipt_document':doc.name}, pluck='parent')
    for i in list(set(lcv)):
        frappe.delete_doc_if_exists('Landed Cost Voucher', i)