# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime
from odoo import SUPERUSER_ID
import time,  pytz,base64
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    @api.onchange('name')
    def _address_home_dom_id(self):
        for patient_data in self:
            patient_data._get_address_dom_Id()
            patient_data.address_home_dom_id = 1

    def _get_address_dom_Id(self):
        partner_ids = []
        for res_user in self.env['res.users'].search([('partner_id', '!=', None)]):
            partner_ids.append(res_user.partner_id.id)
        domain = [('id', 'in', partner_ids)]
        return domain

    address_home_dom_id = fields.Char('Private Address domain', compute='_address_home_dom_id')
    address_home_id = fields.Many2one(
        'res.partner', 'Private Address',
        help='Enter here the private address of the employee, not the one linked to your company.',
        domain=_get_address_dom_Id)

    qatar_id = fields.Char('Qatar ID')
    no_check_in_today = fields.Boolean('Not Check-in Today', compute='_compute_un_check_in_employee',
                                       search='_search_un_check_in_employee')
    document_ids = fields.One2many('employee.document', 'employee_id', string='Documents')
    show_documents = fields.Boolean('Able to see Documents', compute='_compute_show_documents')
    bank_id = fields.Many2one('res.bank', related='bank_account_id.bank_id', string="Bank", copy=False)
    bank_code = fields.Char(related='bank_id.bank_code', string='Short Name')
    iban_code = fields.Char(string='IBAN Code', required=True)

    @api.model
    def create(self, values):
        if values.get('name') and not values.get('address_home_id'):
            private_address = self.env['res.partner'].create({'name': values.get('name')})
            values['address_home_id'] = private_address.id
        res = super(HrEmployee, self).create(values)
        return res

    @api.multi
    def write(self, values):
        if values.get('name'):
            self.address_home_id.write({'name': values.get('name')})
        res = super(HrEmployee, self).write(values)
        return res

    @api.multi
    def _compute_un_check_in_employee(self):
        today_date = datetime.utcnow().date()
        today_start = fields.Datetime.to_string(today_date)  # get the midnight of the current utc day
        today_end = fields.Datetime.to_string(today_date + relativedelta(hours=23, minutes=59, seconds=59))
        for employee in self:
            attendance = self.env['hr.attendance'].search([
                ('employee_id', 'in', employee.ids),
                ('check_in', '<=', today_end),
                ('check_in', '>=', today_start),
            ])
            if attendance:
                employee.no_check_in_today = False
            else:
                employee.no_check_in_today = True

    @api.multi
    def _search_un_check_in_employee(self, operator, value):
        today_date = datetime.utcnow().date()
        today_start = fields.Datetime.to_string(today_date)  # get the midnight of the current utc day
        today_end = fields.Datetime.to_string(today_date + relativedelta(hours=23, minutes=59, seconds=59))
        holidays = self.env['hr.attendance'].sudo().search([
            ('employee_id', '!=', False),
            ('check_in', '<=', today_end),
            ('check_in', '>=', today_start),
        ])
        return [('id', 'not in', holidays.mapped('employee_id').ids)]

    @api.multi
    def _compute_show_documents(self):
        show_documents = self.env['res.users'].has_group('hr.group_hr_manager') or \
                         self.env['res.users'].has_group('hr.group_hr_user')
        for employee in self:
            if show_documents or employee.user_id == self.env.user:
                employee.show_documents = True
            else:
                employee.show_documents = False



    @api.model
    def employee_documents_alert(self, cron_mode=True):
        for employee in self.search([('active', '=', True), ('document_ids', '!=', None)]):
            for documents in employee.document_ids:
                if documents.remind_x_day_before>=0:
                    notify_date = (date.today() + timedelta(days=documents.remind_x_day_before)).strftime('%Y-%m-%d')
                    if notify_date == documents.expiry_date:
                        message = documents.document_type.name + ' of ' + employee.name + \
                                  ' (ID: ' + documents.name + ') is going to be expire on ' + documents.expiry_date
                        self.env.user.notify_info(message, title= documents.document_type.name + ' Expiry Alert',
                                                  sticky=True)

    @api.model
    def employee_documents_alert_record_creation(self, cron_mode=True):

        # info = {'content': []}
        dict_doc_type = {}

        for all_documents in self.env['document.type'].search([]):
            list_documents = []
            for employee in self.search([('active', '=', True), ('document_ids', '!=', None)]):
                for documents in employee.document_ids:
                    if documents.document_type.id == all_documents.id and documents.remind_x_day_before>=0:
                        notify_date = (date.today() + timedelta(days=documents.remind_x_day_before)).strftime('%Y-%m-%d')
                        if notify_date == documents.expiry_date:
                            list_documents.append(documents.id)
                    if documents.document_type.id == all_documents.id and date.today() > datetime.strptime(documents.expiry_date, '%Y-%m-%d').date():
                            list_documents.append(documents.id)
            dict_doc_type[all_documents] = list_documents
        newly_created = []
        for key, value in dict_doc_type.items():
            if value:
                created_rec = self.env['employee.expiry.alert'].create({
                    'name': key.id,
                    'expiry_document_ids': [(6, 0, value)],
                })
                newly_created.append(created_rec.id)
        for rec in self.env['employee.expiry.alert'].search([]):
            if rec.id not in newly_created:
                rec.unlink()



    @api.model
    def employee_documents_alert_mail(self, cron_mode=True):
        sl_no_going = 0
        sl_no_expired = 0
        body_html = ""
        expired_message = "<br/> <b>Expired Documents:</b><br/>"
        going_To_alert_message = ""
        for employee in self.search([('active', '=', True), ('document_ids', '!=', None)]):
            for documents in employee.document_ids:
                if documents.remind_x_day_before>=0:
                    notify_date = (date.today() + timedelta(days=documents.remind_x_day_before)).strftime('%Y-%m-%d')
                    if notify_date == documents.expiry_date:
                        sl_no_going += 1
                        message = str(sl_no_going) + "). " + documents.document_type.name + ' of ' + employee.name + \
                                  ' (ID: ' + documents.name + ') is going to be expire on ' + documents.expiry_date
                        message_here = message + """ <br/>"""
                        going_To_alert_message += message_here
                if date.today() > datetime.strptime(documents.expiry_date,'%Y-%m-%d').date():
                    sl_no_expired += 1
                    message_ex = str(sl_no_expired) + "). " + documents.document_type.name + ' of ' + employee.name + \
                              ' (ID: ' + documents.name + ') expired on ' + documents.expiry_date
                    message_here_ex = message_ex + """ <br/>"""
                    expired_message += message_here_ex
        mail_to_hr = self.env['ir.config_parameter'].sudo().get_param('hr_complete_solution.mail_to_hr')
        head_html = """<div>
                                                    <p>Hello,</p>
                                                    <p>This email was created automatically.</p>
                                                </div><br/>"""
        footer_html = """<br/><div>Thank You</div>"""
        if sl_no_expired:
            body_html = head_html +  str(going_To_alert_message) + str(expired_message) + footer_html
        if not sl_no_expired:
            body_html = head_html +  str(going_To_alert_message) + footer_html
        from_email = mail_to_hr
        mail_values = {
            'reply_to': from_email,
            'email_to': from_email,
            'subject': 'Alert Notification: ',
            'body_html': body_html,
        }
        mail_id = self.env['mail.mail'].create(mail_values)
        mail_id.send()
        if mail_id.state == 'exception':
            message = mail_id.failure_reason
            self.env.user.notify_warning(message, title='Mail Delivery Failed !!!', sticky=True)
        else:
            message = "Document Alert mail sent successfully."
            self.env.user.notify_info(message, title='Email sent', sticky=True)

    @api.model
    def attendance_report_alert_mail(self, cron_mode=True):
        date_from = time.strftime('%Y-%m-%d 20:00:00')
        date_to = time.strftime('%Y-%m-%d 19:59:59')
        date_from = str(datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S') + relativedelta(days=-1))

        data = {'date_from': date_from, 'date_to': date_to, 'employee_id': False}
        # here................
        data.update({'form': data})
        user = self.env['res.users'].browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        start_date = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
        start_date = pytz.utc.localize(start_date).astimezone(tz)
        start_date = start_date.replace(tzinfo=None)+ timedelta(hours=1)
        end_date = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
        end_date = pytz.utc.localize(end_date).astimezone(tz)
        end_date = end_date.replace(tzinfo=None)+ timedelta(hours=1)
        REPORT_ID = 'hr_complete_solution.action_report_attendancee'
        pdf = self.env.ref(REPORT_ID).render_qweb_pdf(self.ids, data=data)
        b64_pdf = base64.b64encode(pdf[0])
        # print fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(here_date_from)))
        ATTACHMENT_NAME = 'Attendance Report: ' + str(start_date) + " To " + str(end_date)
        attachment_id = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'datas_fname': ATTACHMENT_NAME + '.pdf',
            # 'store_fname': ATTACHMENT_NAME + '.pdf',
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        mail_to_hr = self.env['ir.config_parameter'].sudo().get_param('hr_complete_solution.mail_to_hr')

        from_email = mail_to_hr
        mail_values = {
            'reply_to': from_email,
            'email_to': from_email,
            'subject': ATTACHMENT_NAME,
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

    def attendance_report_alert_all(self, date_from):
        # machines = self.env['zk.machine'].search([])
        # for machine in machines:
        #     machine.download_attendance()
        date_from1 = date_from
        date_from = date_from + " 00:00:00"
        today = datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')
        start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        start = start - timedelta(hours=3)
        stop = start + timedelta(days=1)
        data = {'date_from': str(start), 'date_to': str(stop), 'employee_id': False}
        data.update({'form': data})
        REPORT_ID = 'hr_complete_solution.action_report_attendancee'
        pdf = self.env.ref(REPORT_ID).render_qweb_pdf(self.ids, data=data)
        b64_pdf = base64.b64encode(pdf[0])
        ATTACHMENT_NAME = 'Attendance Report: ' + str(date_from1)
        attachment_id = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'datas_fname': ATTACHMENT_NAME + '.pdf',
            # 'store_fname': ATTACHMENT_NAME + '.pdf',
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        mail_to_hr = self.env['ir.config_parameter'].sudo().get_param('hr_complete_solution.mail_to_hr')
        from_email = mail_to_hr
        mail_values = {
            'reply_to': from_email,
            'email_to': from_email,
            'subject': ATTACHMENT_NAME,
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

    @api.model
    def attendance_report_alert_mail_today(self, cron_mode=True):
        date_from = time.strftime('%Y-%m-%d')
        self.attendance_report_alert_all(date_from)

    @api.model
    def attendance_report_alert_mail_yesterday(self, cron_mode=True):
        today_date = datetime.utcnow().date()
        today_end = fields.Datetime.to_string(today_date + relativedelta(days=-1))
        today_end = datetime.strptime(today_end, "%Y-%m-%d %H:%M:%S").date()
        today_end = today_end.strftime("%Y-%m-%d")
        self.attendance_report_alert_all(today_end)



