import os
import frappe
from frappe.utils import get_url
from pyqrcode import create as qrcreate


def qrcode_as_png(invoice, content):
    """Save temporary Qrcode to server."""
    png_file_name = "{}.png".format(invoice+'_payment_url')
    old_file = frappe.db.get_value('File', {"attached_to_field":'qr_code'}, 'name')
    if(old_file):
        frappe.delete_doc('File', old_file)
    print(old_file)
    _file = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": png_file_name,
            "attached_to_doctype": "Sales Invoice",
            "attached_to_name": invoice,
            "content": png_file_name,
            "attached_to_field":'qr_code',
        }
    )
    _file.save()
    print(_file.name)
    frappe.db.commit()
    file_url = get_url(_file.file_url)
    file_path = os.path.join(frappe.get_site_path("public", "files"), _file.file_name)
    print(file_path)
    url = qrcreate(content)
    with open(file_path, "wb") as png_file:
        url.png(png_file, scale=8)
    return _file.file_url