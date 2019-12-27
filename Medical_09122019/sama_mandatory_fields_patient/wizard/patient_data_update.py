from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class UpdateWizard(models.TransientModel):
    _name = 'patient.data.update'

    @api.model
    def _get_default_nationality(self):
        default_auType =self.env['patient.nationality'].search([('name', '=', 'qatari')])
        return default_auType

    appt_id = fields.Many2one('medical.appointment', 'Appointment', required=True)
    patient_name = fields.Char("Patient Name")
    patient_phone = fields.Char("Patient Phone")
    qid = fields.Char("QID")
    sex = fields.Selection([('m', 'Male'), ('f', 'Female'), ], 'Gender')
    dob = fields.Date('Date of Birth')
    nationality_id = fields.Many2one('patient.nationality', 'Nationality', default=_get_default_nationality)
    patient_type = fields.Selection([('qat', 'Qatari'), ('reside', 'Resident'), ('vist', 'Visit')],
                                    'Patient Type',required=True, default='qat',track_visibility='onchange')

    @api.multi
    
    def action_Update_checkin(self):
        wizard_vals = self.read()[0]
        if wizard_vals['appt_id']:
            appointment = self.env['medical.appointment'].browse(wizard_vals['appt_id'][0])
            patient_vals = {}
            appointment_vals = {}
            if wizard_vals['patient_name']:
                patient_vals['patient_name'] = wizard_vals['patient_name']
                appointment_vals['patient_name'] = wizard_vals['patient_name']
            if wizard_vals['qid']:
                patient_vals['qid'] = wizard_vals['qid']
                appointment_vals['qid'] = wizard_vals['qid']
            if wizard_vals['sex']:
                patient_vals['sex'] = wizard_vals['sex']
                appointment_vals['sex'] = wizard_vals['sex']
            if wizard_vals['dob']:
                patient_vals['dob'] = wizard_vals['dob']
                appointment_vals['dob'] = wizard_vals['dob']
            if wizard_vals['nationality_id']:
                patient_vals['nationality_id'] = wizard_vals['nationality_id'][0]
                appointment_vals['nationality_id'] = wizard_vals['nationality_id'][0]
            if wizard_vals['patient_type']:
                patient_vals['patient_type'] = wizard_vals['patient_type']
                appointment_vals['patient_type'] = wizard_vals['patient_type']
            if appointment.patient:
                if wizard_vals['patient_phone']:
                    patient_vals['mobile'] = wizard_vals['patient_phone']
                appointment.patient.write(patient_vals)
                appointment.patient.onchange_patient_name()
            else:
                if wizard_vals['patient_phone']:
                    appointment_vals['patient_phone'] = wizard_vals['patient_phone']
            appointment.write(appointment_vals)
            appointment.checkin()

