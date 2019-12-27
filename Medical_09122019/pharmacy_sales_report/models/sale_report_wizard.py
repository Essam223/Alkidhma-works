from odoo import api, fields, models, SUPERUSER_ID
import base64
from odoo.exceptions import Warning
from datetime import datetime


class SalesReportWizard(models.TransientModel):
    _name = "pharmacy.sales.report"

    period_start = fields.Date("Period From", required=True, default=fields.Date.context_today)
    period_stop = fields.Date("Period To", required=True, default=fields.Date.context_today)
    show_drug = fields.Boolean("Show Drug Details ?", default=True)

    @api.multi
    def send_pharmacy_sales_report(self):
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'show_drug': self.show_drug
        }
        report_id = 'pharmacy_sales_report.pharmacy_sales_report'
        pdf = self.env.ref(report_id).render_qweb_pdf(self.ids, data=data)
        b64_pdf = base64.b64encode(pdf[0])
        attachment_name = 'Pharmacy Sales Report: ' + str(self.period_start) + " To " + str(self.period_stop)
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
            <p>This email was created automatically by Odoo H Care. Please find the attached Pharmacy sales reports.</p>
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
    def pharmacy_sales_report(self):
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'show_drug': self.show_drug
                }
        return self.env.ref('pharmacy_sales_report.pharmacy_sales_report').report_action(self, data=data)


class ReportSale(models.AbstractModel):
    _name = 'report.pharmacy_sales_report.pharmacy_sales_report_pdf'

    @api.model
    def get_sale_details(self,period_start=False, period_stop=False, show_drug=False):
        dom = [
                ('date_order', '>=', period_start),
                ('date_order', '<=', period_stop),
                ('is_pharmacy', '=', True),
                ('state', 'in', ('sale', 'done'))
            ]
        orders_new = self.env['sale.order'].search(dom)
        order_list = []
        for order in orders_new:
            invoice = False
            for inv in order.invoice_ids:
                if inv.state in ('open', 'paid'):
                    invoice = inv
            if invoice:
                result = invoice._get_payments_vals()
                cash = 0.0
                credit = 0.0
                disc_total = 0.0
                lines = []
                for line in invoice.invoice_line_ids:
                    line_disc = 0
                    if line.discount_value:
                        disc_total += line.discount_value
                        line_disc += line.discount_value
                    if line.discount:
                        amt_value = line.price_unit * line.quantity * line.discount * line.amt_paid_by_patient
                        line_disc += amt_value / 10000
                        disc_total += amt_value / 10000
                    lines.append((line.product_id.name_get()[0][1], line.price_unit * line.quantity, line_disc))
                if invoice.discount_value:
                    disc_total += invoice.discount_value
                if invoice.discount:
                    order_amount_total = invoice.amount_untaxed + invoice.amount_tax
                    disc_total += (order_amount_total * invoice.discount or 0.0) / 100.0
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
                due = order.amount_total - cash - credit
                if not show_drug:
                    lines = []
                order_data = {
                    'name': order.name,
                    'partner_id': order.partner_id.name,
                    'user_id': order.user_id.name,
                    'date_order': order.date_order,
                    'amount_total': order.amount_total,
                    'cash': cash,
                    'credit': credit,
                    'due': due,
                    'lines': lines,
                    'disc_total': disc_total,
                    'initial_amt': order.amount_total + disc_total,
                }
                order_list.append(order_data)
        return {
            'orders': sorted(order_list, key=lambda l: l['name'])
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_sale_details(data['period_start'],
                                          data['period_stop'],
                                          data['show_drug']
                                          ))
        data['period_start'] = datetime.strptime(data['period_start'], '%Y-%m-%d')
        data['period_stop'] = datetime.strptime(data['period_stop'], '%Y-%m-%d')
        return data
