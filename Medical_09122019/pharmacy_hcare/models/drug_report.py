from odoo import api, fields, models, tools, _


class DrugLabel(models.AbstractModel):
    _name = 'report.pharmacy_hcare.drug_print_pdf'

    @api.model
    def get_drug_details(self, ids=False):
        appt = self.env['medical.appointment'].search([('id', '=', ids)])
        record = {'records': []}
        for pres in appt.prescription_ids:
            if pres.common_dosage:
                frequency = pres.common_dosage.name
                record['records'].append(frequency)
        return record

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_drug_details(data['ids'][0]))
        return data