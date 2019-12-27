from odoo import api, fields, models, SUPERUSER_ID
import base64
from odoo.exceptions import Warning
from datetime import datetime


class ReportSummary(models.AbstractModel):
    _name = 'report.monthly_summary_report.summary_report_pdf'

    @api.model
    def get_summary_details(self,period_start=False, period_stop=False):
        dom_invoice = [
            ('date_invoice', '>=', period_start),
            ('date_invoice', '<=', period_stop),
            ('type', 'in', ('out_invoice', 'out_refund')),
            ('is_patient', '=', True),
            ('state', 'in', ('open', 'paid'))
        ]
        invoices = self.env['account.invoice'].search(dom_invoice)
        dom_payment = [
            ('payment_date', '>=', period_start),
            ('payment_date', '<=', period_stop),
            ('partner_type', '=', 'customer'),
            ('state', 'in', ('posted', 'reconciled'))
        ]
        payments = self.env['account.payment'].search(dom_payment)
        journal_obj = self.env['account.journal']
        cash_journals = journal_obj.search([('type', '=', 'cash')]).ids
        bank_journals = journal_obj.search([('type', '=', 'bank')]).ids
        date_list = []
        for inv in invoices:
            if inv.date_invoice not in date_list:
                date_list.append(inv.date_invoice)
        for payment in payments:
            if payment.payment_date not in date_list:
                date_list.append(payment.payment_date)

        order_list = []
        for date in date_list:
            inv_data = {'date': date, 'sales_sum': 0.0, 'cash': 0.0, 'card': 0.0}
            order_list.append(inv_data)
        for inv in invoices:
            for vals in order_list:
                if vals['date'] == inv.date_invoice:
                    if inv.type == 'out_invoice':
                        vals['sales_sum'] += inv.amount_total
                    else:
                        if inv.amount_total:
                            vals['sales_sum'] += -1 * inv.amount_total

        for payment in payments:
            order = False
            if len(payment.invoice_ids) == 1:
                order = payment.invoice_ids
                flag = 0
                if not order.is_patient:
                    flag = 1
                if flag == 0:
                    for vals in order_list:
                        if vals['date'] == payment.payment_date:
                            if order.type == 'out_invoice':
                                if payment.journal_id.id in cash_journals:
                                    vals['cash'] += payment.amount
                                if payment.journal_id.id in bank_journals:
                                    vals['card'] += payment.amount
                            else:
                                if payment.amount:
                                    if payment.journal_id.id in cash_journals:
                                        vals['cash'] += -1 * payment.amount
                                    if payment.journal_id.id in bank_journals:
                                        vals['card'] += -1 * payment.amount
        return {
            'orders': sorted(order_list, key=lambda l: l['date']),
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_summary_details(
                                          data['period_start'],
                                          data['period_stop']))
        data['period_start'] = datetime.strptime(data['period_start'], '%Y-%m-%d')
        data['period_stop'] = datetime.strptime(data['period_stop'], '%Y-%m-%d')
        return data
