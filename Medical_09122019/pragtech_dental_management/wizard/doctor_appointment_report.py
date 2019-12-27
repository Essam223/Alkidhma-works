from odoo import api, fields, models
from datetime import datetime, timedelta


class DoctorAppointmentWizard(models.TransientModel):
    _name = "doctor.appointment.report"

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

    is_only_doctor = fields.Boolean()
    period_start = fields.Datetime("Period From", required=True, default=_get_start_time)
    period_stop = fields.Datetime("Period To", required=True, default=_get_end_time)
    doctor = fields.Many2one('medical.physician', "Doctor", domain=_get_doctor_id)

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

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.doctor and self.doctor.company_id != self.company_id:
            self.doctor = False
        domain = self._get_doctor_id()
        return {
            'domain': {'doctor': domain}
        }

    @api.model
    def default_get(self, fields):
        res = super(DoctorAppointmentWizard, self).default_get(fields)
        self._get_company_id()
        res['company_id'] = self.env.user.company_id.id
        res['is_only_doctor'] = False
        self._get_doctor_id()
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
    def doctor_appointment_report(self):
        doctor = False
        if self.doctor:
            doctor = [self.doctor.id, self.doctor.name.name]
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'doctor': doctor,
            'company_id': [self.company_id.id, self.company_id.name],
                }
        return self.env.ref('pragtech_dental_management.report_doctor_appointment_pdf').report_action(self, data=data)


class ReportDoctorAppointment(models.AbstractModel):

    _name = 'report.pragtech_dental_management.report_doctor_appointment'

    @api.model
    def get_appt_details(self, period_start=False, period_stop=False, doctor=False, company_id=False):
        dom = [
            ('appointment_sdate', '>=', period_start),
            ('appointment_edate', '<=', period_stop),
            ('company_id', '=', company_id[0]),
        ]
        if doctor:
            dom.append(('doctor', '=', doctor[0]))
        doctors = self.env['medical.physician'].search([('company_id', '=', company_id[0])])
        doctrs = []
        doctrs_list = []
        appts = {}
        for i in doctors:
            doctrs.append(i)
            appts[i] = []
        appointments = self.env['medical.appointment'].search(dom, order="appointment_sdate asc")
        for app in appointments:
            appts[app.doctor].append(app)
        for each in doctrs:
            appts[each] = appts.pop(each)
            doctrs_list.append(each)
        period_start = datetime.strptime(period_start, '%Y-%m-%d %H:%M:%S')
        period_stop = datetime.strptime(period_stop, '%Y-%m-%d %H:%M:%S')
        return {
            'period_start': period_start,
            'period_stop': period_stop,
            'doctor': doctor,
            'doctors': doctrs_list,
            'appointments': appts
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_appt_details(data['period_start'],
                                          data['period_stop'], data['doctor'], data['company_id']))
        return data
