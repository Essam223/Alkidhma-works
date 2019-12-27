from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class ConsentForFinalCementation(models.TransientModel):
    _name = 'consent.final.cementation'

    language = fields.Selection([('english', 'English'),
                                 ('arabic', 'Arabic')], 'Language', required=True, default='english')
    register_date = fields.Date('Date', default=fields.Date.context_today, required=True)
    patient_id = fields.Many2one('medical.patient', 'Patient', required=True)
    doctor_id = fields.Many2one('medical.physician', 'Doctor')
    Parent_Guardian = fields.Char('Parent/Guardian')
    Treatment = fields.Char('Treatment')
    Tooth_number = fields.Char('Tooth number')

    Patient_or_Guardian_signature = fields.Binary(string='Patient/Legal Guardian Signature')
    Treating_Dentist_signature = fields.Binary(string='Doctor Signature')
    Witness_signature = fields.Binary(string='Witness Signature')
    Patient_or_Guardian_signature2 = fields.Binary(string='Patient/Legal Guardian Signature')
    Treating_Dentist_signature2 = fields.Binary(string='Doctor Signature')
    Witness_signature2 = fields.Binary(string='Witness Signature')

    @api.multi
    def action_confirm(self):
        wizard_vals = self.read()[0]
        if self.language == 'arabic':
            wizard_vals['Patient_or_Guardian_signature'] = self.Patient_or_Guardian_signature2
            wizard_vals['Treating_Dentist_signature'] = self.Treating_Dentist_signature2
            wizard_vals['Witness_signature'] = self.Witness_signature2
        self.patient_id.attach_Consent_for_Final_Cementation(self.register_date, wizard_vals)


class ReportConsentForFinalCementation(models.AbstractModel):
    _name = 'report.consent_management.report_final_cementation'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['medical.patient'].browse(data['ids'])
        return {
            'doc_ids': self.ids,
            'doc_model': 'consent.final.cementation',
            'data': data,
            'docs': docs,
            'language': data['wizard_vals']['language'],
            'doctor_id': data['wizard_vals']['doctor_id'],
            'Treatment': data['wizard_vals']['Treatment'],
            'Tooth_number': data['wizard_vals']['Tooth_number'],
            'Parent_Guardian': data['wizard_vals']['Parent_Guardian'],
            'register_date': data['wizard_vals']['register_date'],
            'Patient_or_Guardian_signature': data['wizard_vals']['Patient_or_Guardian_signature'],
            'Treating_Dentist_signature': data['wizard_vals']['Treating_Dentist_signature'],
            'Witness_signature': data['wizard_vals']['Witness_signature'],
        }