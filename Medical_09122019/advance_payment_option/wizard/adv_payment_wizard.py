from odoo import api, fields, models, SUPERUSER_ID
import base64
from odoo.exceptions import Warning
from datetime import datetime


class AdvancePaymentReportWizard(models.TransientModel):
    _name = "advance.payment.report"

    period_start = fields.Date("Period From", required=True, default=fields.Date.context_today)
    period_stop = fields.Date("Period To", required=True, default=fields.Date.context_today)
    patient = fields.Many2one('res.partner', "Patient", domain=[('is_patient', '=', True)])

    @api.multi
    def sale_report(self):
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'patient_id': self.patient.id,
            'patient': self.patient.name,
                }
        return self.env.ref('advance_payment_option.advance_payment_report').report_action(self, data=data)


class ReportAdvPayment(models.AbstractModel):
    _name = 'report.advance_payment_option.advance_payment_report_pdf'

    @api.model
    def get_adv_payment_details(self, period_start=False, period_stop=False, patient_id=False, patient=False):
        dom = [
            ('payment_date', '>=', period_start),
            ('payment_date', '<=', period_stop),
            ('partner_type', '=', 'customer'),
            ('advance', '=', True),
            ('state', 'in', ('posted', 'reconciled'))
        ]
        if patient:
            dom.append(('partner_id', '=', patient_id))
        payment_records = self.env['account.payment'].search(dom)
        order_list = []
        cash_count = 0
        card_count = 0
        for payment in payment_records:
            pay_mode = False
            cash = 0
            credit = 0
            journal_obj = self.env['account.journal']
            cash_journals = journal_obj.search([('type', '=', 'cash')]).ids
            bank_journals = journal_obj.search([('type', '=', 'bank')]).ids
            if payment.journal_id.id in cash_journals:
                cash += payment.amount
                cash_count += 1
                pay_mode = 'cash'
            if payment.journal_id.id in bank_journals:
                credit += payment.amount
                card_count += 1
                pay_mode = 'card'
            if payment.payment_type == 'inbound':
                order_data = {
                    'name': payment.name,
                    'journal_id': payment.journal_id.name,
                    'payment_date': payment.payment_date,
                    'patient': payment.partner_id.name,
                    'type': 'out_invoice',
                    'cash': cash,
                    'credit': credit,
                    'pay_mode': pay_mode,
                    'amount': payment.amount,
                }
            else:
                if cash:
                    cash = -cash
                if credit:
                    credit = -credit
                order_data = {
                    'name': payment.name,
                    'journal_id': payment.journal_id.name,
                    'payment_date': payment.payment_date,
                    'patient': payment.partner_id.name,
                    'type': 'out_refund',
                    'cash': cash,
                    'credit': credit,
                    'pay_mode': pay_mode,
                    'amount': -payment.amount,
                }
            if order_data:
                order_list.append(order_data)
        return {
            'orders': sorted(order_list, key=lambda l: l['name']),
            'period_start':  period_start,
            'period_stop':  period_stop,
            'payment_mode':  False,
            'cash': cash_count,
            'card': card_count,
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_adv_payment_details(data['period_start'],
                                          data['period_stop'],
                                          data['patient_id'],
                                          data['patient'],
                                          ))
        data['period_start'] = datetime.strptime(data['period_start'], '%Y-%m-%d')
        data['period_stop'] = datetime.strptime(data['period_stop'], '%Y-%m-%d')
        return data
