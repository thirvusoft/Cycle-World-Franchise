// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Online Sales Series', {
	abbreviation(frm) {
		frm.call({
			doc:frm.doc,
			method: "preview_series",
			args:{abbr: frm.doc.abbreviation},
			callback: function(r) {
				if (!r.exc) {
					frm.set_value("series_preview", r.message);
				} else {
					frm.set_value("series_preview", __("Failed to generate preview of series"));
				}
			}
		});
	},
});

