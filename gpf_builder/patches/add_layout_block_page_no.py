import frappe


def execute():
	if not frappe.db.has_column("GPF Layout Block", "page_no"):
		frappe.db.sql("alter table `tabGPF Layout Block` add column `page_no` int not null default 1")

	frappe.db.sql(
		"""
		update `tabGPF Layout Block`
		set page_no = 1
		where ifnull(page_no, 0) < 1
		"""
	)
