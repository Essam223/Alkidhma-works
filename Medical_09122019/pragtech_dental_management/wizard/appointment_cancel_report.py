from odoo import api, fields, models
from datetime import datetime, timedelta


class AppointmentCancelWizard(models.TransientModel):
    _name = "appointment.cancel.report"

    def _get_start_time(self):
        start_time = datetime.now()
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = start_time - timedelta(hours=3)
        return start_time

    def _get_end_time(self):
        start_time = datetime.now()
        end_time = start_time.replace(hour=20, minute=59, second=59, microsecond=0)
        return end_time

    def _get_doctor_id(self):
        domain = []
        doc_ids = None
        group_dental_doc_menu = self.env.user.has_group('pragtech_dental_management.group_dental_doc_menu')
        group_dental_user_menu = self.env.user.has_group('pragtech_dental_management.group_dental_user_menu')
        group_dental_mng_menu = self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu')
        if group_dental_doc_menu and not group_dental_user_menu and not group_dental_mng_menu:
            dom_partner = [('user_id', '=', self.env.user.id), ('is_doctor', '=', True),
                           ('company_id', '=', self.company_id.id)]
            partner_ids = [x.id for x in self.env['res.partner'].search(dom_partner)]
            if partner_ids:
                doc_ids = [x.id for x in self.env['medical.physician'].search([('name', 'in', partner_ids),
                                                                              ('company_id', '=', self.company_id.id)])]
        else:
            doc_ids = [x.id for x in self.env['medical.physician'].search([('company_id', '=', self.company_id.id)])]
        domain = [('id', 'in', doc_ids)]
        return domain

    def _get_responsible_person_id(self):
        domain = [('company_id', '=', self.company_id.id)]
        return domain

    def _get_patient_id(self):
        domain = [('company_id', '=', self.company_id.id)]
        return domain

    is_only_doctor = fields.Boolean()
    period_start = fields.Datetime("Period From", required=True, default=_get_start_time)
    period_stop = fields.Datetime("Period To", required=True, default=_get_end_time)
    doctor = fields.Many2one('medical.physician', "Doctor", domain=_get_doctor_id)
    patient = fields.Many2one('medical.patient', "Patient", domain=_get_patient_id)
    responsible_person = fields.Many2one('res.users', string='Responsible Person', domain=_get_responsible_person_id)

    def _get_company_id(self):
        domain_company = []
        company_ids = None
        group_multi_company = self.env.user.has_group('base.group_multi_company')
        if group_multi_company:
            company_ids = [x.id for x in self.env['res.company'].search([('id', 'in', self.env.user.company_ids.ids)])]
            domain_company = [('id', 'in', company_ids)]
        else:
            domain_company = [('id', '=', self.env.user.company_id.id)]
        return domain_company

    company_id = fields.Many2one('res.company', "Company", domain=_get_company_id, required=True)

    @api.onchange('patient')
    def onchange_patient(self):
        if self.patient and self.patient.company_id != self.company_id:
            self.patient = False

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.doctor and self.doctor.company_id != self.company_id:
            self.doctor = False
        if self.patient and self.patient.company_id != self.company_id:
            self.patient = False
        if self.responsible_person and self.responsible_person.company_id != self.company_id:
            self.responsible_person = False
        doctor_domain = self._get_doctor_id()
        patient_domain = self._get_patient_id()
        responsible_person_domain = self._get_responsible_person_id()
        return {
            'domain': {'doctor': doctor_domain, 'patient':patient_domain, 'responsible_person': responsible_person_domain}
        }

    @api.model
    def default_get(self, fields):
        res = super(AppointmentCancelWizard, self).default_get(fields)
        self._get_company_id()
        res['company_id'] = self.env.user.company_id.id
        res['is_only_doctor'] = False
        self._get_doctor_id()
        self._get_patient_id()
        self._get_responsible_person_id()
        doc_ids = None
        group_dental_doc_menu = self.env.user.has_group('pragtech_dental_management.group_dental_doc_menu')
        group_dental_user_menu = self.env.user.has_group('pragtech_dental_management.group_dental_user_menu')
        group_dental_mng_menu = self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu')
        if group_dental_doc_menu and not group_dental_user_menu and not group_dental_mng_menu:
            res['is_only_doctor'] = True
            dom_partner = [('user_id', '=', self.env.user.id), ('is_doctor', '=', True),
                           ('company_id', '=', self.env.user.company_id.id)]
            partner_ids = [x.id for x in self.env['res.partner'].search(dom_partner)]
            if partner_ids:
                doc_ids = [x.id for x in self.env['medical.physician'].search([('name', 'in', partner_ids)])]
        if doc_ids:
            res['doctor'] = doc_ids[0]
        return res

    @api.multi
    def appointment_cancel_report(self):
        doctor = False
        patient = False
        responsible_person = False
        if self.doctor:
            doctor = [self.doctor.id, self.doctor.name.name]
        if self.patient:
            name = self.patient.name.name
            if self.patient.patient_id:
                name = '[' + self.patient.patient_id + ']' + name
            patient = [self.patient.id, name]
        if self.responsible_person:
            responsible_person = [self.responsible_person.id, self.responsible_person.name]
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'patient': patient,
            'responsible_person': responsible_person,
            'doctor': doctor,
            'company_id': [self.company_id.id, self.company_id.name],
                }
        return self.env.ref('pragtech_dental_management.report_appt_cancellation_pdf').report_action(self, data=data)


class ReportAppointmentCancellation(models.AbstractModel):

    _name = 'report.pragtech_dental_management.report_appt_cancellation'

    @api.model
    def get_appt_cancel_details(self, period_start=False, period_stop=False, doctor=False, patient=False,
                         responsible_person=False, company_id=False):
        dom = [
            ('appointment_sdate', '>=', period_start),
            ('appointment_edate', '<=', period_stop),
            ('state', '=', 'cancel'),
            ('company_id', '=', company_id[0]),
        ]
        if doctor:
            dom.append(('doctor', '=', doctor[0]))
        if patient:
            dom.append(('patient', '=', patient[0]))
        if responsible_person:
            dom.append(('responsible_person', '=', responsible_person[0]))
        appointments = self.env['medical.appointment'].search(dom, order="appointment_sdate asc")
        period_start = datetime.strptime(period_start, '%Y-%m-%d %H:%M:%S')
        period_stop = datetime.strptime(period_stop, '%Y-%m-%d %H:%M:%S')
        return {
            'period_start': period_start,
            'period_stop': period_stop,
            'doctor': doctor,
            'patient': patient,
            'responsible_person': responsible_person,
            'appointments': appointments
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_appt_cancel_details(data['period_start'],
                                          data['period_stop'], data['doctor'], data['patient'],
                                          data['responsible_person'],
                                          data['company_id']))
        return data
