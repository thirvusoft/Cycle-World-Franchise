import frappe
from datetime import datetime

def after_insert(self, event=None):
    self.valid_from = datetime.now()
    self.save()