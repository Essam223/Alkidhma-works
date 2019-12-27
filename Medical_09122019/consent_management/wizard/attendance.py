from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class AttendanceConsent(models.TransientModel):
    _name = 'attendance.consent'

    language = fields.Selection([('english', 'English'),
                                 ('arabic', 'Arabic')], 'Language', required=True, default='english')
    register_date = fields.Date('Date', default=fields.Date.context_today, required=True)
    patient_id = fields.Many2one('medical.patient', 'Patient', required=True)
    doctor_id = fields.Many2one('medical.physician', 'Doctor')

    # treatment_id = fields.Many2one('product.product', 'Treatment', required=True, domain=[('is_treatment', '=', True)])

    Parent_Guardian = fields.Char('Parent/Guardian')
    Treatment = fields.Char('Treatment')
    Tooth_number = fields.Char('Tooth number')

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.patient_name = self.patient_id.name.name

    patient_name = fields.Char('Patient', required=True, size=60)

    @api.multi
    def action_confirm(self):
        wizard_vals = self.read()[0]
        self.patient_id.attach_attendance(self.register_date, wizard_vals)


class ReportAttendance(models.AbstractModel):
    _name = 'report.consent_management.report_attendance_pdf'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['medical.patient'].browse(data['ids'])
        return {
            'doc_ids': self.ids,
            'doc_model': 'attendance.consent',
            'data': data,
            'docs': docs,
            'language': data['wizard_vals']['language'],
            'doctor_id': data['wizard_vals']['doctor_id'],
            'register_date': data['wizard_vals']['register_date'],
            # 'treatment_id': data['wizard_vals']['treatment_id'],
            'Treatment': data['wizard_vals']['Treatment'],
            'Tooth_number': data['wizard_vals']['Tooth_number'],
            'Parent_Guardian': data['wizard_vals']['Parent_Guardian'],
        }