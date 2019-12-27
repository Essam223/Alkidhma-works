from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class ConsentDerma(models.TransientModel):
    _name = 'consent.derma'

    language = fields.Selection([('english', 'English'),
                                 ('arabic', 'Arabic')], 'Language', required=True, default='english')
    register_date = fields.Date('Date', default=fields.Date.context_today, required=True)
    patient_id = fields.Many2one('medical.patient', 'Patient', required=True)
    doctor_id = fields.Many2one('medical.physician', 'Doctor')
    age = fields.Char('Age')
    pregnant = fields.Char('Pregnant or Lactating, If Applicable')
    treatment = fields.Char('Treatment')
    indication = fields.Char('Indication')

    Patient_or_Guardian_signature = fields.Binary(string='Patient/Guardian Signature')
    Treating_Dentist_signature = fields.Binary(string='Doctor Signature')
    Patient_or_Guardian_signature2 = fields.Binary(string='Patient/Guardian Signature')
    Treating_Dentist_signature2 = fields.Binary(string='Doctor Signature')

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
        if self.language == 'arabic':
            wizard_vals['Patient_or_Guardian_signature'] = self.Patient_or_Guardian_signature2
            wizard_vals['Treating_Dentist_signature'] = self.Treating_Dentist_signature2
        self.patient_id.attach_consent_derma(self.register_date, wizard_vals)


class ReportConsentDerma(models.AbstractModel):
    _name = 'report.sama_consent_management.report_derma'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['medical.patient'].browse(data['ids'])
        return {
            'doc_ids': self.ids,
            'doc_model': 'consent.derma',
            'data': data,
            'docs': docs,
            'language': data['wizard_vals']['language'],
            'doctor_id': data['wizard_vals']['doctor_id'],
            'age': data['wizard_vals']['age'],
            'pregnant': data['wizard_vals']['pregnant'],
            'treatment': data['wizard_vals']['treatment'],
            'indication': data['wizard_vals']['indication'],
            'register_date': data['wizard_vals']['register_date'],
            'Patient_or_Guardian_signature': data['wizard_vals']['Patient_or_Guardian_signature'],
            'Treating_Dentist_signature': data['wizard_vals']['Treating_Dentist_signature'],
        }
