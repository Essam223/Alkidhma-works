# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


# class AppontmentsCalendar(models.Model):
#     _inherit = 'appointments.calendar'
#
#     def find_hcare_groups(self):
#         is_group = False
#         # Admin/Receptionist/Nurse
#         if self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu') or \
#                 self.env.user.has_group('pragtech_dental_management.group_dental_user_menu') or \
#                 self.env.user.has_group('medical.group_dental_nurse_menu'):
#             is_group = True
#         return is_group


class MedicalAppointment(models.Model):
    _inherit = "medical.appointment"

    def find_hcare_groups(self):
        is_group = False
        # Admin/Receptionist/Nurse
        if self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu') or \
                self.env.user.has_group('pragtech_dental_management.group_dental_user_menu') or \
                self.env.user.has_group('medical.group_dental_nurse_menu'):
            is_group = True
        return is_group

    def show_wiz_clinic_Assessment(self):
        view_id = self.env.ref('medical.medical_appointment_view_clinical_Assessment').id
        context = self._context.copy()
        return {
            'name': 'Clinical Assessment',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'medical.appointment',
            'view_id': view_id,
            'domain': [],
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
            'context': context,
        }

    dental = fields.Boolean('Dental', default=False, compute='_compute_dental_doctor')

    @api.depends('doctor')
    def _compute_dental_doctor(self):
        for record in self:
            if record.doctor:
                if record.doctor.dental:
                    record.dental = True
                else:
                    record.dental = False
            else:
                record.dental = False

    @api.multi
    def print_patient_file(self):
        datas = {'doctor': self.doctor.name.name, 'appointment_sdate': self.appointment_sdate,
                 'id_patient': self.patient.id}
        values = self.env.ref('medical.action_report_patient_file').report_action(self.patient.id,
                                                                                             data=datas)
        return values

    READONLY_STATES_APPOINT = {
        'done': [('readonly', True)],
        'visit_closed': [('readonly', True)],
    }

    def _get_nurse_id(self):
        company = self.env['res.company']._company_default_get('res.partner')
        if self.company_id:
            company = self.company_id
        domain = [('company_id', '=', company.id)]
        return domain

    @api.onchange('company_id')
    def onchange_company_id(self):
        user = super(MedicalAppointment, self).onchange_company_id()
        if self.nurse_id and self.nurse_id.company_id != self.company_id:
            self.nurse_id = False
        nurse_domain = self._get_nurse_id()
        user['domain']['nurse_id'] = nurse_domain
        return user

    weight = fields.Float(readonly=False)
    temp = fields.Char(readonly=False)
    hr = fields.Char('HR', readonly=False)
    rr = fields.Char('RR', readonly=False)
    bp = fields.Char('BP', readonly=False)
    sp02 = fields.Char('SP02', readonly=False)
    Laboratory = fields.Text(readonly=False)
    LaboratoryAttach = fields.Binary('Laboratory Attachment', readonly=False)
    ECG = fields.Text('ECG', readonly=False)
    ECGAttach = fields.Binary('ECG Attachment', readonly=False)
    Echocardiography = fields.Text(readonly=False)
    EchocardiographyAttach = fields.Binary('Echocardiography Attachment', readonly=False)
    Radiology = fields.Text(readonly=False)
    RadiologyAttach = fields.Binary('Radiology Attachment', readonly=False)
    StressTest = fields.Text('Stress Test', readonly=False)
    StressTestAttach = fields.Binary('Stress Test Attachment', readonly=False)
    vital_sign = fields.Boolean(default=False)
    nurse_id = fields.Many2one('medical.nurse', 'Attended Nurse', domain=_get_nurse_id)

    def CollectedVitalSigns(self):
        if self.env.user.has_group('medical.group_dental_nurse_menu'):
            nurses = self.env['medical.nurse'].search([('nurse', '=', self.env.uid)]).ids
            if nurses:
                self.nurse_id = nurses[0]
        self.vital_sign = True

    def ModifyVitalSigns(self):
        self.vital_sign = False
