import frappe

def execute():
	"""
	Create or retrieve the single active MVP setup idempotently.
	Ensures target_doctype is hard-restricted to 'Dunning Letter'.
	"""
	if not frappe.db.exists("GPF Print Format Setup", {"target_doctype": "Dunning Letter"}):
		setup = frappe.new_doc("GPF Print Format Setup")
		setup.target_doctype = "Dunning Letter"
		setup.status = "Editing"
		setup.insert(ignore_permissions=True)
	else:
		# Ensure existing setup is correctly configured for MVP
		setup = frappe.get_doc("GPF Print Format Setup", {"target_doctype": "Dunning Letter"})
		if setup.target_doctype != "Dunning Letter":
			setup.target_doctype = "Dunning Letter"
			setup.save(ignore_permissions=True)
