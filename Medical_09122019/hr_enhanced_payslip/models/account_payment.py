# -*- coding: utf-8 -*-
import datetime, time
from dateutil import relativedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payslip_ids = fields.Many2many('hr.payslip', 'payslip_payment_rel', 'payment_id', 'payslip_id',
                                   string="Payslips", copy=False, readonly=True)

    def _compute_journal_domain_and_types(self):
        rec = super(AccountPayment, self)._compute_journal_domain_and_types()
        if self.payslip_ids:
            domain = []
            journal_type = ['bank', 'cash']
            if self.currency_id.is_zero(self.amount):
                # In case of payment with 0 amount, allow to select a journal of type 'general' like
                # 'Miscellaneous Operations' and set this journal by default.
                journal_type = ['general']
                self.payment_difference_handling = 'reconcile'
            else:
                if self.payment_type == 'inbound':
                    domain.append(('at_least_one_inbound', '=', True))
                else:
                    domain.append(('at_least_one_outbound', '=', True))
            return {'domain': domain, 'journal_types': set(journal_type)}
        return rec

    @api.multi
    def delete_payment(self):
        if len(self.payslip_ids) == 1:
            residual = self.payslip_ids.residual + self.amount
            if residual:
                self.payslip_ids.write({ 'state': 'confirmed'})
            else:
                self.payslip_ids.write({'state': 'done'})
        res = super(AccountPayment, self).delete_payment()
        return res

    def _get_counterpart_move_line_vals(self, invoice=False):
        if self.payment_type == 'transfer':
            name = self.name
        else:
            name = ''
            if self.partner_type == 'customer':
                if self.payment_type == 'inbound':
                    name += _("Customer Payment")
                elif self.payment_type == 'outbound':
                    name += _("Customer Credit Note")
            elif self.partner_type == 'supplier':
                if self.payment_type == 'inbound':
                    name += _("Vendor Credit Note")
                elif self.payment_type == 'outbound':
                    if self.payslip_ids:
                        name += _("Salary Payment")
                    else:
                        name += _("Vendor Payment")
            if invoice:
                name += ': '
                for inv in invoice:
                    if inv.move_id:
                        name += inv.number + ', '
                name = name[:len(name)-2]
        return {
            'name': name,
            'account_id': self.destination_account_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

    def action_validate_payslip_payment(self):
        if any(len(record.invoice_ids) > 1 for record in self):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(_("This method should only be called to process a single invoice's payment."))
        self.post()
        payment_amt = self.amount
        if len(self.payslip_ids) == 1:
            if self.amount > self.payslip_ids.net_salary:
                raise UserError(_("Payment amount should not be greater than Payslip amount."))
            residual = self.payslip_ids.residual
            if not residual:
                self.payslip_ids.write({'state': 'done'})
            self.payslip_ids.write({'residual': residual})


    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        payslip_defaults = self.resolve_2many_commands('payslip_ids', rec.get('payslip_ids'))
        if payslip_defaults and len(payslip_defaults) == 1:
            payslip = payslip_defaults[0]
            partner_id = False
            if payslip['employee_id']:
                partner_id = self.env['hr.employee'].browse(payslip['employee_id'][0]).address_home_id.id
            currency_id = False
            if payslip['company_id']:
                currency_id = self.env['res.company'].browse(payslip['company_id'][0]).currency_id.id
            rec['communication'] = payslip['number'] or payslip['name']
            rec['currency_id'] = currency_id
            # rec['payment_type'] = payslip['type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
            rec['payment_type'] = 'outbound'
            rec['partner_type'] = 'supplier'
            rec['partner_id'] = partner_id
            rec['amount'] = payslip['residual']
        return rec