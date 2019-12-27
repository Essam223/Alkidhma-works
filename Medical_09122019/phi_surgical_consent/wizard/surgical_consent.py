from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class SurgicalConsent(models.TransientModel):
    _name = 'surgical.consent'

    language = fields.Selection([('english', 'English'),
                                 ('arabic', 'Arabic')], 'Language', required=True, default='english')
    register_date = fields.Date('Date', default=fields.Date.context_today, required=True)
    patient_id = fields.Many2one('medical.patient', 'Patient', required=True)
    dob = fields.Date('Date of Birth')
    sex = fields.Selection([('m', 'Male'), ('f', 'Female'), ], 'Gender')
    nationality_id = fields.Many2one('patient.nationality', 'Nationality')
    mobile = fields.Char('Contact Number')
    file_number = fields.Char('File Number')
    doctor_id = fields.Many2one('medical.physician', 'Doctor', required=True)
    doctor_name = fields.Many2one('medical.physician', 'Doctor', required=True)
    speciality = fields.Many2one('medical.speciality', 'Specialty')

    surgical_procedure = fields.Text('Surgical procedure')
    Complications_Findings = fields.Text('Complications and findings')
    risk_complications = fields.Text('Risk/Complications')
    alternative_surgical_procedure = fields.Text('Alternative surgical procedure')
    result_without_treatment = fields.Text('Result without treatment')

    Surgeon = fields.Char('Doctor')
    Patient_Guardian = fields.Char('Patient (Guardian)')
    Translator = fields.Char('Translator')

    Surgeon_signature = fields.Binary(string='Doctor Signature')
    Patient_or_Guardian_signature = fields.Binary(string='Patient/Legal Guardian Signature')
    Translator_signature = fields.Binary(string='Translator Signature')
    Surgeon_signature2 = fields.Binary(string='Surgeon Signature')
    Patient_or_Guardian_signature2 = fields.Binary(string='Patient/Legal Guardian Signature')
    Translator_signature2 = fields.Binary(string='Translator Signature')

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.dob = self.patient_id.dob
            self.sex = self.patient_id.sex
            self.nationality_id = self.patient_id.nationality_id.id
            self.mobile = self.patient_id.mobile
            self.file_number = self.patient_id.patient_id

    @api.onchange('doctor_id')
    def onchange_doctor_id(self):
        if self.doctor_id:
            self.speciality = self.doctor_id.speciality
            self.doctor_name = self.doctor_id.id
            self.Surgeon = self.doctor_id.name.name

    @api.multi
    def action_confirm(self):
        wizard_vals = self.read()[0]
        if self.language == 'arabic':
            wizard_vals['Surgeon_signature'] = self.Surgeon_signature2
            wizard_vals['Patient_or_Guardian_signature'] = self.Patient_or_Guardian_signature2
            wizard_vals['Translator_signature'] = self.Translator_signature2
        self.patient_id.attach_surgical_consent(self.register_date, wizard_vals)


class ReportSurgicalConsent(models.AbstractModel):
    _name = 'report.phi_surgical_consent.report_surgical_consent_pdf'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['medical.patient'].browse(data['ids'])
        patient_name = self.env['medical.patient'].browse(data['wizard_vals']['patient_id'][0]).name.name
        speciality = False
        if data['wizard_vals']['speciality']:
            speciality = data['wizard_vals']['speciality'][1]
        nationality = False
        if data['wizard_vals']['nationality_id']:
            nationality = data['wizard_vals']['nationality_id'][1]
        return {
            'doc_ids': self.ids,
            'doc_model': 'surgical.consent',
            'data': data,
            'docs': docs,
            'register_date': data['wizard_vals']['register_date'],
            'language': data['wizard_vals']['language'],
            'patient_id': data['wizard_vals']['patient_id'],
            'patient_name': patient_name,
            'dob': data['wizard_vals']['dob'],
            'sex': data['wizard_vals']['sex'],
            'nationality_id': nationality,
            'mobile': data['wizard_vals']['mobile'],
            'file_number': data['wizard_vals']['file_number'],
            'doctor_id': data['wizard_vals']['doctor_id'],
            'doctor_name': data['wizard_vals']['doctor_name'],
            'speciality': speciality,
            'surgical_procedure': data['wizard_vals']['surgical_procedure'],
            'Complications_Findings': data['wizard_vals']['Complications_Findings'],
            'risk_complications': data['wizard_vals']['risk_complications'],
            'alternative_surgical_procedure': data['wizard_vals']['alternative_surgical_procedure'],
            'result_without_treatment': data['wizard_vals']['result_without_treatment'],

            'Surgeon': data['wizard_vals']['Surgeon'],
            'Patient_Guardian': data['wizard_vals']['Patient_Guardian'],
            'Translator': data['wizard_vals']['Translator'],


            'Surgeon_signature': data['wizard_vals']['Surgeon_signature'],
            'Patient_or_Guardian_signature': data['wizard_vals']['Patient_or_Guardian_signature'],
            'Translator_signature': data['wizard_vals']['Translator_signature'],
        }