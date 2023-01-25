import frappe

def validate(doc, event=None):
    if(doc.get('transportation_cost') or (doc.get('shipping_cost') or 0)):
        doc.additional_cost = (doc.get('transportation_cost') or 0) + (doc.get('shipping_cost') or 0)
    doc.standard_rate = (doc.get('standard_buying_cost') or 0) + (
                        (doc.get('standard_buying_cost') or 0)*(doc.get('ts_margin') or 0)/100) + (doc.get('additional_cost') or 0)
    doc.standard_rate = doc.get('standard_rate') - doc.get('standard_rate')*(doc.get('ts_discount_') or 0)/100 