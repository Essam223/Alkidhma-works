# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import  time,  pytz,base64
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import SUPERUSER_ID
from odoo.exceptions import ValidationError


class ReportAttendance(models.TransientModel):
    _name = 'report.attendance'
    _description = 'Report Attendance'

    def _get_start_time(self):
        start_time = datetime.now()
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = start_time - timedelta(hours=3)
        return start_time

    def _get_end_time(self):
        start_time = datetime.now()
        end_time = start_time.replace(hour=20, minute=59, second=59, microsecond=0)
        return end_time

    employee_id = fields.Many2one('hr.employee', string='Employee')
    date_from = fields.Datetime('Period From', default= _get_start_time, required=True)
    date_to = fields.Datetime('Period To', required=True, default=_get_end_time)

    @api.multi
    def action_print_report_attendance(self):
        employee_id = False
        if self.employee_id:
            employee_id = [self.employee_id.id, self.employee_id.name]
        data = {
            'date_start': self.date_from,
            'date_stop': self.date_to,
            'employee_id': employee_id
        }
        return self.env.ref('hr_complete_solution.action_report_attendancee').report_action(self, data=data)

    @api.multi
    def email_report(self):
        employee_id = False
        if self.employee_id:
            employee_id = [self.employee_id.id, self.employee_id.name]
        data = {
            'date_start': self.date_from,
            'date_stop': self.date_to,
            'employee_id': employee_id
        }
        user = self.env['res.users'].browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        start_date = datetime.strptime(self.date_from, "%Y-%m-%d %H:%M:%S")
        start_date = pytz.utc.localize(start_date).astimezone(tz).replace(tzinfo=None)
        end_date = datetime.strptime(self.date_to, "%Y-%m-%d %H:%M:%S")
        end_date = pytz.utc.localize(end_date).astimezone(tz).replace(tzinfo=None)
        report_id = 'hr_complete_solution.action_report_attendancee'
        pdf = self.env.ref(report_id).render_qweb_pdf(self.ids, data=data)
        b64_pdf = base64.b64encode(pdf[0])
        attachment_name = 'Attendance Report: ' + str(start_date) + " To " + str(end_date)
        attachment_id = self.env['ir.attachment'].create({
            'name': attachment_name,
            'type': 'binary',
            'datas': b64_pdf,
            'datas_fname': attachment_name + '.pdf',
            # 'store_fname': attachment_name + '.pdf',
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        mail_to_hr = self.env['ir.config_parameter'].sudo().get_param('hr_complete_solution.mail_to_hr')
        if not mail_to_hr:
            raise ValidationError(_('Configure Sender Mail from HR Settings'))

        from_email = mail_to_hr
        mail_values = {
            'reply_to': from_email,
            'email_to': from_email,
            'subject': attachment_name,
            'body_html': """<div>
                                <p>Hello,</p>
                                <p>This email was created automatically. 
                                Please find the attached Attendance report.</p>
                            </div>
                            <div>Thank You</div>""",
            'attachment_ids': [(4, attachment_id.id)]
        }
        mail_id = self.env['mail.mail'].create(mail_values)
        mail_id.send()
        if mail_id.state == 'exception':
            message = mail_id.failure_reason
            self.env.user.notify_warning(message, title='Mail Delivery Failed !!!', sticky=True)
        else:
            message = "Attendance Report mail sent successfully."
            self.env.user.notify_info(message, title='Email sent', sticky=True)


class ReportParserAttendance(models.AbstractModel):
    _name = 'report.hr_complete_solution.report_attendance'

    @api.model
    def get_report_attendance(self, date_start=False, date_stop=False, employee_id=False):
        dom = ['|', '&', ('check_in', '<=', date_stop), ('check_in', '>=', date_start), '&',
               ('check_out', '<=', date_stop), ('check_out', '>=', date_start)]

        if employee_id:
            dom.append(('employee_id', '=', employee_id[0]))
        attendances = self.env['hr.attendance'].search(dom)
        return {
            'attendances': attendances,
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_report_attendance(data['date_start'],
                                               data['date_stop'],
                                               data['employee_id']))
        return data
