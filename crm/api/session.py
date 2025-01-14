import frappe


@frappe.whitelist()
def get_users():
	if frappe.session.user == "Guest":
		frappe.throw("Authentication failed", exc=frappe.AuthenticationError)

	users = frappe.qb.get_query(
		"User",
		fields=["name", "email", "enabled", "user_image", "full_name", "user_type"],
		order_by="full_name asc",
		distinct=True,
	).run(as_dict=1)

	for user in users:
		if frappe.session.user == user.name:
			user.session_user = True
	return users

@frappe.whitelist()
def get_contacts():
	if frappe.session.user == "Guest":
		frappe.throw("Authentication failed", exc=frappe.AuthenticationError)

	contacts = frappe.qb.get_query(
		"Contact",
		fields=['name', 'full_name', 'image', 'email_id', 'mobile_no', 'phone', 'salutation'],
		order_by="first_name asc",
		distinct=True,
	).run(as_dict=1)

	return contacts