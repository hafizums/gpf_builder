import frappe


def execute():
	if not frappe.db.has_column("GPF Layout Block", "is_locked"):
		frappe.db.sql("alter table `tabGPF Layout Block` add column `is_locked` int not null default 0")

	frappe.db.sql(
		"""
		update `tabGPF Layout Block`
		set is_locked = 0
		where is_locked is null
		"""
	)
