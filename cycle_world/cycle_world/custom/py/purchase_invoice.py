import frappe
import json

def create_landed_voucher(doc, event = None):
    """on_submit Event"""
    # frappe.db.commit()
    if isinstance(doc, str):
        doc = json.loads(doc)
        doc = frappe.get_doc(doc)
    purchase_doc = frappe.get_doc(doc.doctype, doc.name)
    if(len(purchase_doc.landed_cost_taxes)==0):
        return
    if(doc.doctype=='Purchase Invoice'):
        if(doc.update_stock != 1):
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
        'taxes':purchase_doc.landed_cost_taxes
    })
    lnd_doc.save()
    lnd_doc.submit()

def on_cancel(doc, event=None):
    lcv = frappe.db.get_all('Landed Cost Purchase Receipt', filters={'receipt_document_type':doc.doctype, 'receipt_document':doc.name, 'docstatus':1}, pluck='parent')
    for i in list(set(lcv)):
        lnd = frappe.get_doc('Landed Cost Voucher', i)
        lnd.cancel()

def on_trash(doc, event=None):
    lcv = frappe.db.get_all('Landed Cost Purchase Receipt', filters={'receipt_document_type':doc.doctype, 'receipt_document':doc.name}, pluck='parent')
    for i in list(set(lcv)):
        frappe.delete_doc_if_exists('Landed Cost Voucher', i)