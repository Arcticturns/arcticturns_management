app_name = "arcticturns_management"
app_title = "arcticturns_management"
app_publisher = "arcticturns"
app_description = "The Basic Arcticturns Management"
app_email = "pugazhenthi.arcticturns@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/arcticturns_management/css/arcticturns_management.css"
# app_include_js = "/assets/arcticturns_management/js/arcticturns_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/arcticturns_management/css/arcticturns_management.css"
# web_include_js = "/assets/arcticturns_management/js/arcticturns_management.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "arcticturns_management/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Timesheet": "public/js/timesheet_task.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "arcticturns_management.utils.jinja_methods",
# 	"filters": "arcticturns_management.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "arcticturns_management.install.before_install"
# after_install = "arcticturns_management.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "arcticturns_management.uninstall.before_uninstall"
# after_uninstall = "arcticturns_management.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "arcticturns_management.utils.before_app_install"
# after_app_install = "arcticturns_management.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "arcticturns_management.utils.before_app_uninstall"
# after_app_uninstall = "arcticturns_management.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "arcticturns_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Timesheet": {
		"validate": "arcticturns_management.timesheet_validation.validate_timesheet",
		"before_submit": "arcticturns_management.timesheet_validation.validate_timesheet",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"arcticturns_management.tasks.all"
# 	],
# 	"daily": [
# 		"arcticturns_management.tasks.daily"
# 	],
# 	"hourly": [
# 		"arcticturns_management.tasks.hourly"
# 	],
# 	"weekly": [
# 		"arcticturns_management.tasks.weekly"
# 	],
# 	"monthly": [
# 		"arcticturns_management.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "arcticturns_management.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "arcticturns_management.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "arcticturns_management.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["arcticturns_management.utils.before_request"]
# after_request = ["arcticturns_management.utils.after_request"]

# Job Events
# ----------
# before_job = ["arcticturns_management.utils.before_job"]
# after_job = ["arcticturns_management.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"arcticturns_management.auth.validate"
# ]
page_renderer = ["arcticturns_management.essl_renderer.ESSLADMSRenderer"]

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [[
			"name",
			"in",
			[
				"Timesheet-workflow_state",
				"Timesheet-salary_slip",
				"Timesheet-custom_expected_hours",
				"Timesheet-custom_leave__holiday_work_reason",
				"Timesheet-custom_shortfall_reason",
			],
		]],
	},
	{
		"dt": "Workflow",
		"filters": [["document_type", "=", "Timesheet"]],
	},
	{
		"dt": "Workflow State",
		"filters": [["name", "in", ["Draft", "Submitted", "Approved", "Rejected", "Cancelled"]]],
	},
	{
		"dt": "Workflow Action Master",
		"filters": [["name", "in", ["Submit", "Approve", "Reject", "Resubmit", "Cancel"]]],
	},
	{
		"dt": "Role",
		"filters": [["name", "=", "AT Timesheet Approver"]],
	},
	{
		"dt": "Property Setter",
		"filters": [["doc_type", "in", ["Timesheet", "Timesheet Detail"]]],
	},
	{
		"dt": "Custom DocPerm",
		"filters": [["parent", "in", ["Timesheet", "Task"]]],
	},
]
