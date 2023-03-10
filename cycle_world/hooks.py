from . import __version__ as app_version

app_name = "cycle_world"
app_title = "Cycle World"
app_publisher = "Thirvusoft"
app_description = "Cycle World"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "thirvusoft@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/cycle_world/css/cycle_world.css"
app_include_js = "/assets/cycle_world/js/item_quick_entry.js"

# include js, css files in header of web template
# web_include_css = "/assets/cycle_world/css/cycle_world.css"
# web_include_js = "/assets/cycle_world/js/cycle_world.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "cycle_world/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
			"Item" : "cycle_world/custom/js/item.js",
			"Contact" :"cycle_world/custom/js/contact.js",
			"Purchase Invoice" : "cycle_world/custom/js/purchase_invoice.js",
			"Purchase Receipt" : "cycle_world/custom/js/purchase_receipt.js",
			"Item Attribute" : "cycle_world/custom/js/item_attribute.js",
			"Company":'cycle_world/custom/js/company.js',
            "Stock Reconciliation":"cycle_world/item_rename/stock_reconciliation.js",
            "Branch":"cycle_world/custom/js/branch.js"
			}
doctype_list_js = {"Item" : "cycle_world/custom/js/item_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "cycle_world.install.before_install"
after_install = "cycle_world.install.after_install"
after_migrate = "cycle_world.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "cycle_world.uninstall.before_uninstall"
# after_uninstall = "cycle_world.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "cycle_world.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Item": "cycle_world.cycle_world.custom.py.item.CycleWorldItem"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Invoice": {
		"validate": "cycle_world.cycle_world.custom.py.sales_invoice.validate",
        "autoname": "cycle_world.cycle_world.custom.py.sales_invoice.auto_name",
	},
	"User":{
		'validate': 'cycle_world.cycle_world.user_permissions.user.validate',
        'after_insert': 'cycle_world.cycle_world.user_permissions.user.validate',
	},
	"Branch":{
		'validate':'cycle_world.cycle_world.user_permissions.branch.validate'
	},
	"Item":{
		'validate':'cycle_world.cycle_world.custom.py.item.validate',
		'after_insert':'cycle_world.cycle_world.custom.py.item.validate',
		'autoname':'cycle_world.cycle_world.custom.py.item.autoname',
	},
	"Item Attribute":{
		'validate':'cycle_world.cycle_world.custom.py.item_attribute.validate'
	},
	"Purchase Invoice":{
		'on_submit':'cycle_world.cycle_world.custom.py.purchase_invoice.create_landed_voucher',
		'on_cancel':'cycle_world.cycle_world.custom.py.purchase_invoice.on_cancel',
		'on_trash':'cycle_world.cycle_world.custom.py.purchase_invoice.on_trash'
	},
	"Purchase Receipt":{
		'on_submit':'cycle_world.cycle_world.custom.py.purchase_invoice.create_landed_voucher',
		'on_cancel':'cycle_world.cycle_world.custom.py.purchase_invoice.on_cancel',
		'on_trash':'cycle_world.cycle_world.custom.py.purchase_invoice.on_trash'
	},
	"Landed Cost Voucher":{
		'on_submit':'cycle_world.cycle_world.custom.py.item.item_price_update'
	},
	"Item Price":{
		'after_insert':'cycle_world.cycle_world.custom.py.item_price.after_insert'
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"cycle_world.tasks.all"
#	],
#	"daily": [
#		"cycle_world.tasks.daily"
#	],
#	"hourly": [
#		"cycle_world.tasks.hourly"
#	],
#	"weekly": [
#		"cycle_world.tasks.weekly"
#	]
#	"monthly": [
#		"cycle_world.tasks.monthly"
#	]
# }

# Testing
# -------

# before_tests = "cycle_world.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.controllers.item_variant.enqueue_multiple_variant_creation": "cycle_world.cycle_world.custom.py.item_variant.enqueue_multiple_variant_creation",
	"frappe.desk.search.search_link":"cycle_world.cycle_world.custom.py.search.search_link"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "cycle_world.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"cycle_world.auth.validate"
# ]

