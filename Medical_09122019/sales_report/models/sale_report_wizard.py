from odoo import api, fields, models, SUPERUSER_ID
import base64
from odoo.exceptions import Warning
from datetime import datetime


class SalesReportWizard(models.TransientModel):
    _name = "sale.report.wizard"

    def _get_payment_mode_id(self):
        domain = [('invoice_journal', '=', True), ('type', 'in', ('bank', 'cash')),
                  ('company_id', '=', self.company_id.id)]
        return domain

    def _get_insurance_company_id(self):
        domain = [('is_insurance_company', '=', True),('company_id', '=', self.company_id.id)]
        return domain

    def _get_cashier_id(self):
        domain = [('company_id', '=', self.company_id.id)]
        return domain

    def _get_patient_id(self):
        domain = [('company_id', '=', self.company_id.id)]
        return domain

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
    date_type = fields.Selection([('invoice', 'Invoice Date'),
                                  ('payment', 'Payment Date')],
                                 string='Based on', required=True, default='payment')
    period_start = fields.Date("Period From", required=True, default=fields.Date.context_today)
    period_stop = fields.Date("Period To", required=True, default=fields.Date.context_today)
    doctor = fields.Many2one('medical.physician', "Doctor", domain=_get_doctor_id)
    patient = fields.Many2one('medical.patient', "Patient", domain=_get_patient_id)
    cashier = fields.Many2one('res.users', 'Cashier', domain=_get_cashier_id)
    payment_mode = fields.Many2one('account.journal', 'Payment Mode', domain=_get_payment_mode_id)
    insurance_company = fields.Many2one('res.partner', 'Insurance Company', domain=_get_insurance_company_id)
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
        if self.cashier and self.cashier.company_id != self.company_id:
            self.cashier = False
        if self.insurance_company and self.insurance_company.company_id != self.company_id:
            self.insurance_company = False
        if self.payment_mode and self.payment_mode.company_id != self.company_id:
            self.payment_mode = False
        doctor_domain = self._get_doctor_id()
        patient_domain = self._get_patient_id()
        cashier_domain = self._get_cashier_id()
        insurance_company_domain = self._get_insurance_company_id()
        payment_mode_domain = self._get_payment_mode_id()
        return {
            'domain': {'doctor': doctor_domain, 'patient':patient_domain, 'cashier': cashier_domain,
                       'insurance_company':insurance_company_domain, 'payment_mode': payment_mode_domain}
        }

    @api.model
    def default_get(self, fields):
        res = super(SalesReportWizard, self).default_get(fields)
        self._get_company_id()
        res['company_id'] = self.env.user.company_id.id
        res['is_only_doctor'] = False
        self._get_doctor_id()
        self._get_patient_id()
        self._get_cashier_id()
        self._get_insurance_company_id()
        self._get_payment_mode_id()
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
    def send_sale_report(self):
        doctor = False
        payment_mode = False
        if self.doctor:
            doctor = [self.doctor.id, self.doctor.name.name]
        cashier = False
        if self.cashier:
            cashier = [self.cashier.id, self.cashier.name]
        if self.payment_mode:
            payment_mode = [self.payment_mode.id, self.payment_mode.name, self.payment_mode.type]
        insurance_company = False
        if self.insurance_company:
            insurance_company = [self.insurance_company.id, self.insurance_company.name]
        patient = False
        if self.patient:
            name = self.patient.name.name
            if self.patient.patient_id:
                name = '[' + self.patient.patient_id + ']' + name
            patient = [self.patient.id, name]
        data = {
            'date_type': self.date_type,
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'doctor': doctor,
            'patient': patient,
            'insurance_company': insurance_company,
            'payment_mode': payment_mode,
            'cashier': cashier,
            'company_id': [self.company_id.id, self.company_id.name],
        }
        report_id = 'sales_report.sales_report'
        pdf = self.env.ref(report_id).render_qweb_pdf(self.ids, data=data)
        b64_pdf = base64.b64encode(pdf[0])
        attachment_name = 'Sales Report: ' + str(self.period_start) + " To " + str(self.period_stop)
        attachment_id = self.env['ir.attachment'].create({
            'name': attachment_name,
            'type': 'binary',
            'datas': b64_pdf,
            'datas_fname': attachment_name + '.pdf',
            # 'store_fname': attachment_name,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        attach = {
            attachment_id.id,
        }
        user = self.env['res.users'].browse(SUPERUSER_ID)
        from_email = user.partner_id.email
        mail_values = {
            'reply_to': from_email,
            'email_to': from_email,
            'subject': attachment_name,
            'body_html': """<div>
            <p>Hello,</p>
            <p>This email was created automatically by Odoo H Care. Please find the attached sales reports.</p>
                            </div>
                            <div>Thank You</div>""",
            'attachment_ids': [(6, 0, attach)]
        }
        mail_id = self.env['mail.mail'].create(mail_values)
        mail_id.send()
        if mail_id.state == 'exception':
            message = mail_id.failure_reason
            raise Warning(message)
            # self.env.user.notify_warning(message, title='Mail Delivery Failed !!!', sticky=True)
        else:
            message = "Daily report mail sent successfully."
            self.env.user.notify_info(message, title='Email sent', sticky=True)

    @api.multi
    def sale_report(self):
        doctor = False
        cashier = False
        if self.cashier:
            cashier = [self.cashier.id, self.cashier.name]
        payment_mode = False
        if self.doctor:
            doctor = [self.doctor.id, self.doctor.name.name]
        if self.payment_mode:
            payment_mode = [self.payment_mode.id, self.payment_mode.name, self.payment_mode.type]
        insurance_company = False
        if self.insurance_company:
            insurance_company = [self.insurance_company.id, self.insurance_company.name]
        patient = False
        if self.patient:
            name = self.patient.name.name
            if self.patient.patient_id:
                name = '[' + self.patient.patient_id + ']' + name
            patient = [self.patient.id, name]
        date_type = 'Invoice Date'
        if self.date_type == 'payment':
            date_type = 'Payment Date'
        data = {
            'date_type': date_type,
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'doctor': doctor,
            'patient': patient,
            'insurance_company': insurance_company,
            'payment_mode': payment_mode,
            'cashier': cashier,
            'company_id': [self.company_id.id, self.company_id.name],
                }
        return self.env.ref('sales_report.sales_report').report_action(self, data=data)


class ReportSale(models.AbstractModel):

    _name = 'report.sales_report.sales_report_pdf'

    @api.model
    def get_sale_details(self, date_type=False, period_start=False, period_stop=False, doctor=False, patient=False,
                         insurance_company=False, payment_mode=False, cashier=False, company_id=False):
        if date_type == 'Invoice Date':
            dom = [
                ('date_invoice', '>=', period_start),
                ('date_invoice', '<=', period_stop),
                ('company_id', '=', company_id[0]),
                ('type', 'in', ('out_invoice', 'out_refund')),
                ('is_patient', '=', True),
                ('state', 'in', ('open', 'paid'))
            ]
            if doctor:
                dom.append(('dentist', '=', doctor[0]))
            if patient:
                dom.append(('patient', '=', patient[0]))
            if insurance_company:
                dom.append(('insurance_company', '=', insurance_company[0]))
            orders_new = self.env['account.invoice'].search(dom)
            order_list = []
            for order in orders_new:
                patient_name = False
                if order.patient:
                    nam = order.patient.name.name
                    patient_name = '[' + order.patient.patient_id + ']' + nam
                result = order._get_payments_vals()
                cash = 0.0
                credit = 0.0
                disc_total = 0.0
                for line in order.invoice_line_ids:
                    if line.discount_value:
                        disc_total += line.discount_value
                    if line.discount:
                        disc_total += (line.price_unit*line.quantity*line.discount*line.amt_paid_by_patient)/10000
                if order.discount_value:
                    disc_total += order.discount_value
                if order.discount:
                    order_amount_total = order.amount_untaxed + order.amount_tax
                    disc_total += (order_amount_total * order.discount or 0.0) / 100.0
                move_lin_obj = self.env['account.move.line']
                journal_obj = self.env['account.journal']
                cash_journals = journal_obj.search([('type', '=', 'cash')]).ids
                bank_journals = journal_obj.search([('type', '=', 'bank')]).ids
                for pay in result:
                    move_line_obj = move_lin_obj.browse(pay['payment_id'])
                    if move_line_obj.journal_id.id in cash_journals:
                        cash += pay['amount']
                    if move_line_obj.journal_id.id in bank_journals:
                        credit += pay['amount']
                if order.type == 'out_invoice':
                    order_data = {
                        'number': order.number,
                        'patient': patient_name,
                        'doctor': order.dentist and order.dentist.name and order.dentist.name.name or False,
                        'insurance_company': order.insurance_company and order.insurance_company.name or False,
                        'date_invoice': order.date_invoice,
                        'insurance_total': order.insurance_total,
                        'amount_total': order.amount_total,
                        'type': order.type,
                        'cash': cash,
                        'credit': credit,
                        'disc_total': disc_total,
                        'due': order.residual_signed,
                        'initial_amt': order.amount_total + disc_total + order.insurance_total + order.treatment_group_disc_total,
                        'treatment_group_disc_total': order.treatment_group_disc_total
                    }
                else:
                    insurance_total = amount_total = treatment_group_disc_total = 0.0
                    if order.insurance_total:
                        insurance_total = -1 * order.insurance_total
                    if order.amount_total:
                        amount_total = -1 * order.amount_total
                    if cash:
                        cash = -cash
                    if credit:
                        credit = -credit
                    if disc_total:
                        disc_total = -disc_total
                    if order.treatment_group_disc_total:
                        treatment_group_disc_total = -1 * order.treatment_group_disc_total
                    order_data = {
                        'number': order.number,
                        'patient': patient_name,
                        'doctor': order.dentist and order.dentist.name and order.dentist.name.name or False,
                        'insurance_company': order.insurance_company and order.insurance_company.name or False,
                        'date_invoice': order.date_invoice,
                        'insurance_total': insurance_total,
                        'amount_total': amount_total,
                        'type': order.type,
                        'cash': cash,
                        'credit': credit,
                        'disc_total': disc_total,
                        'due': order.residual_signed,
                        'initial_amt': amount_total + disc_total + insurance_total + treatment_group_disc_total,
                        'treatment_group_disc_total': treatment_group_disc_total
                    }
                order_list.append(order_data)
        else:
            dom = [
                ('payment_date', '>=', period_start),
                ('payment_date', '<=', period_stop),
                ('partner_type', '=', 'customer'),
                ('company_id', '=', company_id[0]),
                ('state', 'in', ('posted', 'reconciled'))
            ]
            if payment_mode:
                dom.append(('journal_id', '=', payment_mode[0]))
            if cashier:
                dom.append(('create_uid', '=', cashier[0]))
            payment_records = self.env['account.payment'].search(dom)
            order_list = []
            for payment in payment_records:
                cash = 0
                credit = 0
                journal_obj = self.env['account.journal']
                cash_journals = journal_obj.search([('type', '=', 'cash')]).ids
                bank_journals = journal_obj.search([('type', '=', 'bank')]).ids
                if payment.journal_id.id in cash_journals:
                    cash += payment.amount
                if payment.journal_id.id in bank_journals:
                    credit += payment.amount
                if payment.advance:
                    if payment.payment_type == 'inbound':
                        order_data = {
                            'number': payment.name,
                            'bill_date': "",
                            'payment_date': payment.payment_date,
                            'patient': payment.partner_id.name,
                            'doctor': False,
                            'insurance_company': False,
                            'date_invoice': False,
                            'type': 'out_invoice',
                            'cash': cash,
                            'credit': credit,
                            'cashier': payment.create_uid and payment.create_uid.name or False
                        }
                    else:
                        if cash:
                            cash = -cash
                        if credit:
                            credit = -credit
                        order_data = {
                            'number': payment.name,
                            'bill_date': "",
                            'payment_date': payment.payment_date,
                            'patient': payment.partner_id.name,
                            'doctor': False,
                            'insurance_company': False,
                            'date_invoice': False,
                            'type': 'out_refund',
                            'cash': cash,
                            'credit': credit,
                            'cashier': payment.create_uid and payment.create_uid.name or False
                        }
                elif len(payment.invoice_ids) == 1:
                    order = payment.invoice_ids
                    flag = 0
                    if not order.is_patient:
                        flag = 1
                    if doctor and order.dentist.id != doctor[0]:
                        flag = 1
                    if patient and order.patient.id != patient[0]:
                        flag = 1
                    if insurance_company and order.insurance_company.id != insurance_company[0]:
                        flag = 1
                    order_data = {}
                    if flag == 0:
                        patient_name = False
                        if order.patient:
                            nam = order.patient.name.name
                            patient_name = '[' + order.patient.patient_id + ']' + nam
                        if order.type == 'out_invoice':
                            order_data = {
                                'number': order.number,
                                'bill_date': order.date_invoice,
                                'payment_date': payment.payment_date,
                                'patient': patient_name,
                                'doctor': order.dentist and order.dentist.name and order.dentist.name.name or False,
                                'insurance_company': order.insurance_company and order.insurance_company.name or False,
                                'date_invoice': order.date_invoice,
                                'type': order.type,
                                'cash': cash,
                                'credit': credit,
                                'cashier': payment.create_uid and payment.create_uid.name or False
                            }
                        else:
                            if cash:
                                cash = -cash
                            if credit:
                                credit = -credit
                            order_data = {
                                'number': order.number,
                                'bill_date': order.date_invoice,
                                'payment_date': payment.payment_date,
                                'patient': patient_name,
                                'doctor': order.dentist and order.dentist.name and order.dentist.name.name or False,
                                'insurance_company': order.insurance_company and order.insurance_company.name or False,
                                'date_invoice': order.date_invoice,
                                'type': order.type,
                                'cash': cash,
                                'credit': credit,
                                'cashier': payment.create_uid and payment.create_uid.name or False
                            }

                else:
                    if payment.payment_type == 'inbound':
                        order_data = {
                            'number': payment.name,
                            'bill_date': "",
                            'payment_date': payment.payment_date,
                            'patient': payment.partner_id.name,
                            'doctor': False,
                            'insurance_company': False,
                            'date_invoice': False,
                            'type': 'out_invoice',
                            'cash': cash,
                            'credit': credit,
                            'cashier': payment.create_uid and payment.create_uid.name or False
                        }
                    else:
                        if cash:
                            cash = -cash
                        if credit:
                            credit = -credit
                        order_data = {
                            'number': payment.name,
                            'bill_date': "",
                            'payment_date': payment.payment_date,
                            'patient': payment.partner_id.name,
                            'doctor': False,
                            'insurance_company': False,
                            'date_invoice': False,
                            'type': 'out_refund',
                            'cash': cash,
                            'credit': credit,
                            'cashier': payment.create_uid and payment.create_uid.name or False
                        }
                if order_data:
                    order_list.append(order_data)
        return {
            'orders': sorted(order_list, key=lambda l: l['number'])
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_sale_details(data['date_type'],
                                          data['period_start'],
                                          data['period_stop'],
                                          data['doctor'], data['patient'],
                                          data['insurance_company'],
                                          data['payment_mode'],
                                          data['cashier'],
                                          data['company_id']))
        # data['period_start'] = datetime.strptime(data['period_start'], '%Y-%m-%d')
        # data['period_stop'] = datetime.strptime(data['period_stop'], '%Y-%m-%d')
        return data
