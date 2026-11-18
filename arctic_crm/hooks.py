app_name = "arctic_crm"
app_title = "Arctic Turns CRM"
app_publisher = "Arctic Turns"
app_description = "Custom CRM for Arctic Turns"
app_email = "moureya.p@arcticturns.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["crm"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "arctic_crm",
# 		"logo": "/assets/arctic_crm/logo.png",
# 		"title": "Arctic Turns CRM",
# 		"route": "/arctic_crm",
# 		"has_permission": "arctic_crm.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/arctic_crm/css/arctic_crm.css"
# app_include_js = "/assets/arctic_crm/js/arctic_crm.js"

# include js, css files in header of web template
# web_include_css = "/assets/arctic_crm/css/arctic_crm.css"
# web_include_js = "/assets/arctic_crm/js/arctic_crm.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "arctic_crm/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "arctic_crm/public/icons.svg"

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

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "arctic_crm.utils.jinja_methods",
# 	"filters": "arctic_crm.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "arctic_crm.install.before_install"
# after_install = "arctic_crm.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "arctic_crm.uninstall.before_uninstall"
# after_uninstall = "arctic_crm.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "arctic_crm.utils.before_app_install"
# after_app_install = "arctic_crm.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "arctic_crm.utils.before_app_uninstall"
# after_app_uninstall = "arctic_crm.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "arctic_crm.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "arctic_crm.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"arctic_crm.tasks.all"
# 	],
# 	"daily": [
# 		"arctic_crm.tasks.daily"
# 	],
# 	"hourly": [
# 		"arctic_crm.tasks.hourly"
# 	],
# 	"weekly": [
# 		"arctic_crm.tasks.weekly"
# 	],
# 	"monthly": [
# 		"arctic_crm.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "arctic_crm.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "arctic_crm.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "arctic_crm.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "arctic_crm.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["arctic_crm.utils.before_request"]
# after_request = ["arctic_crm.utils.after_request"]

# Job Events
# ----------
# before_job = ["arctic_crm.utils.before_job"]
# after_job = ["arctic_crm.utils.after_job"]

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
# 	"arctic_crm.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

doc_events = {
    "CRM Lead": {
        "after_insert": "arctic_crm.tasks.set_first_contact_deadline"
    },
    "CRM Deal": {
        "validate": "arctic_crm.tasks.validate_won_deal_value"
    }
}

scheduler_events = {
    "daily": [
        "arctic_crm.tasks.check_overdue_lead_slas",
        "arctic_crm.tasks.update_sales_target_achievement"
    ]
}
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            ["dt", "in", ["CRM Lead", "CRM Deal", "Sales Target"]]
        ]
    },
    {
        "dt": "Property Setter",
        "filters": [
            ["doc_type", "in", ["CRM Lead", "CRM Deal", "Sales Target"]]
        ]
    },
    {
        "dt": "CRM Fields Layout",
        "filters": [
            ["name", "in", [
                "CRM Deal-Data Fields",
                "CRM Deal-Quick Entry",
                "CRM Deal-Side Panel"
            ]]
        ]
    }
]
permission_query_conditions = {
    "Sales Target": "arctic_crm.permissions.sales_target_permission_query"
}
has_permission = {
    "Sales Target": "arctic_crm.permissions.sales_target_has_permission"
}
