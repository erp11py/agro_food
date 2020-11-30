from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.website.utils import is_signup_enabled
from frappe.utils import cint, flt, has_gravatar, escape_html, format_datetime, now_datetime, get_formatted_email, today
from frappe import utils





@frappe.whitelist(allow_guest=True)
def sign_up(email, full_name, redirect_to,aadhar_card,mobile_number,location,account_name,account_number,branch,ifsc_code):
	if not is_signup_enabled():
		frappe.throw(_('Sign Up is disabled'), title='Not Allowed')

	user = frappe.db.get("User", {"email": email})
	if user:
		if user.disabled:
			return 0, _("Registered but disabled")
		else:
			return 0, _("Already Registered")
	else:
		if frappe.db.sql("""select count(*) from tabUser where
			HOUR(TIMEDIFF(CURRENT_TIMESTAMP, TIMESTAMP(modified)))=1""")[0][0] > 300:

			frappe.respond_as_web_page(_('Temporarily Disabled'),
				_('Too many users signed up recently, so the registration is disabled. Please try back in an hour'),
				http_status_code=429)

		from frappe.utils import random_string
		user = frappe.get_doc({
			"doctype":"User",
			"email": email,
			"first_name": escape_html(full_name),
			"enabled": 1,
			"new_password":"Pk11erp",
			"user_type": "Website User",
			'aadhar_card':aadhar_card,
			'account_name':account_name,
			'account_number':account_number,
			'branch':branch,
			'mobile_no':mobile_number,
			'location':location,
			'ifsc_code':ifsc_code


		})
		user.flags.ignore_permissions = True
		user.flags.ignore_password_policy = True
		user.insert()

		# set default signup role as per Portal Settings
		default_role = frappe.db.get_value("Portal Settings", None, "default_role")
		if default_role:
			user.add_roles(default_role)

		if redirect_to:
			frappe.cache().hset('redirect_after_login', user.name, redirect_to)

		if user.flags.email_sent:
			return 1, _("Please check your email for verification")
		else:
			return 2, _("Please ask your administrator to verify your sign-up")






@frappe.whitelist(allow_guest=True)
def create_po(set_warehouse=None,supplier=None,schedule_date=None,item_code=None,qty=None,rate=None):
	po=address = frappe.get_doc({
		"doctype": "Purchase Order",
		"supplier":supplier,
		"schedule_date":schedule_date,
		"transaction_date":frappe.utils.today(),
		"set_warehouse":set_warehouse
	})
	row =po.append("items", {})
	row.item_code=item_code
	row.qty=qty
	row.rate=rate
	row.schedule_date=schedule_date
	row.warehouse=set_warehouse
	po.flags.ignore_permissions = True
	po.insert()
	return "Purchase Order  created successfully"


   



                