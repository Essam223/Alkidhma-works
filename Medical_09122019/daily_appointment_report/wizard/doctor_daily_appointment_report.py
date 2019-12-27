from odoo import api, fields, models
from datetime import datetime, timedelta


class DoctorAppointmentWizard(models.TransientModel):
    _name = "doctor.daily.appointment.report"

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
    date_appt = fields.Date("Date", required=True, default=fields.Date.context_today)
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
    def doctor_daily_appointment_report(self):
        doctor = False
        if self.doctor:
            doctor = [self.doctor.id, self.doctor.name.name]
        data = {
            'date_appt': self.date_appt,
            'doctor': doctor,
            'company_id': [self.company_id.id, self.company_id.name],
                }
        return self.env.ref('daily_appointment_report.report_doctor_daily_appointment_pdf').report_action(self, data=data)


class ReportDoctorAppointment(models.AbstractModel):

    _name = 'report.daily_appointment_report.report_doctor_daily_appointment'

    def check_appt_in_time(self,appt, date_time):
        appointment_sdate = datetime.strptime(appt.appointment_sdate, '%Y-%m-%d %H:%M:%S')
        date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
        date_time_hour_added = date_time + timedelta(hours=1)
        if date_time <= appointment_sdate < date_time_hour_added:
            return True
        return False

    @api.model
    def get_appt_details(self, date_appt=False, doctor=False, company_id=False):
        dom = [
            ('appointment_sdate', '>=', date_appt),
            ('company_id', '=', company_id[0]),
        ]
        doctors = self.env['medical.physician'].search([('company_id', '=', company_id[0])])
        if doctor:
            dom.append(('doctor', '=', doctor[0]))
            doctors = self.env['medical.physician'].search([('company_id', '=', company_id[0]), ('id', '=', doctor[0])])
        doctrs = []
        doctrs_list = []
        date_new_appt = datetime.strptime(date_appt, '%Y-%m-%d')
        date_new_appt = date_new_appt.replace(hour=9, minute=00)
        date_list = [date_new_appt + timedelta(minutes=60 * x) for x in range(0, 14)]
        time_am_pm_list = [x.strftime('%I:%M %p') for x in date_list]
        date_time_text = [x.strftime('%Y-%m-%d %H:%M:%S') for x in date_list]
        date_appt = datetime.strptime(date_appt, '%Y-%m-%d')
        dr_appts = {}
        for i in doctors:
            doctrs.append(i)
            from collections import OrderedDict
            am_pm_dict = OrderedDict()
            for date_time in date_time_text:
                list_appts = []
                appointments = self.env['medical.appointment'].search(dom, order="appointment_sdate asc")
                for app in appointments:
                    if i == app.doctor:
                        if self.check_appt_in_time(app, date_time):
                            list_appts.append(app)
                am_pm_dict[date_time] = list_appts
            dr_appts[i] = am_pm_dict
        for physician, appt_value in dr_appts.items():
            for key, value in appt_value.items():
                key_date_am_pm = datetime.strptime(key, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
                appt_value[key_date_am_pm] = appt_value.pop(key)
        for each in doctrs:
            dr_appts[each] = dr_appts.pop(each)
            doctrs_list.append(each)
        return {
            'date_appt': date_appt,
            'doctor': doctor,
            'doctors': doctrs_list,
            'dr_appts': dr_appts,
            'time_am_pm_list': time_am_pm_list,
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_appt_details(data['date_appt'], data['doctor'], data['company_id']))
        return data
