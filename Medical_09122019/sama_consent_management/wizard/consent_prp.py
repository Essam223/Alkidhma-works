from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class ConsentPrp(models.TransientModel):
    _name = 'consent.prp'

    language = fields.Selection([('english', 'English'),
                                 ('arabic', 'Arabic')], 'Language', readonly=True, required=True, default='english')
    register_date = fields.Date('Date', default=fields.Date.context_today, required=True)
    patient_id = fields.Many2one('medical.patient', 'Patient', required=True)
    doctor_id = fields.Many2one('medical.physician', 'Doctor')
    age = fields.Char('Age')
    pregnant = fields.Char('Pregnant or Lactating, If Applicable')

    Patient_or_Guardian_signature = fields.Binary(string='Patient/Guardian Signature')
    Treating_Dentist_signature = fields.Binary(string='Doctor Signature')

    @api.onchange('patient_id')
    def _onchange_patient(self):
        if self.patient_id:
            if self.patient_id.dob:
                age = self.patient_id.age
                year, mnth, date = age.partition(' ')
                self.age = year
            else:
                self.age = ''

    @api.multi
    def action_confirm(self):
        wizard_vals = self.read()[0]
        self.patient_id.attach_consent_prp(self.register_date, wizard_vals)


class ReportConsentPrp(models.AbstractModel):
    _name = 'report.sama_consent_management.report_prp'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['medical.patient'].browse(data['ids'])
        return {
            'doc_ids': self.ids,
            'doc_model': 'consent.prp',
            'data': data,
            'docs': docs,
            'language': data['wizard_vals']['language'],
            'doctor_id': data['wizard_vals']['doctor_id'],
            'age': data['wizard_vals']['age'],
            'pregnant': data['wizard_vals']['pregnant'],
            'register_date': data['wizard_vals']['register_date'],
            'Patient_or_Guardian_signature': data['wizard_vals']['Patient_or_Guardian_signature'],
            'Treating_Dentist_signature': data['wizard_vals']['Treating_Dentist_signature'],
        }
