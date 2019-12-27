# -*- coding: utf-8 -*-
import datetime, time
from dateutil import relativedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    termination_ids = fields.Many2many('termination.details', 'termination_payment_rel', 'payment_id', 'termination_id',
                                   string="Termination details", copy=False, readonly=True)

    def _compute_journal_domain_and_types(self):
        rec = super(AccountPayment, self)._compute_journal_domain_and_types()
        if self.termination_ids:
            journal_type = ['bank', 'cash']
            domain = []
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

    # def _get_counterpart_move_line_vals(self, invoice=False):
    #     if self.payment_type == 'transfer':
    #         name = self.name
    #     else:
    #         name = ''
    #         if self.partner_type == 'customer':
    #             if self.payment_type == 'inbound':
    #                 name += _("Customer Payment")
    #             elif self.payment_type == 'outbound':
    #                 name += _("Customer Credit Note")
    #         elif self.partner_type == 'supplier':
    #             if self.payment_type == 'inbound':
    #                 name += _("Vendor Credit Note")
    #             elif self.payment_type == 'outbound':
    #                 if self.payslip_ids:
    #                     name += _("Salary Payment")
    #                 else:
    #                     name += _("Vendor Payment")
    #         if invoice:
    #             name += ': '
    #             for inv in invoice:
    #                 if inv.move_id:
    #                     name += inv.number + ', '
    #             name = name[:len(name)-2]
    #     return {
    #         'name': name,
    #         'account_id': self.destination_account_id.id,
    #         'journal_id': self.journal_id.id,
    #         'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
    #     }

    def action_validate_termination_payment(self):
        self.post()
        if len(self.termination_ids) == 1:
            if self.amount > self.termination_ids.gratuity_amt:
                raise UserError(_("Payment amount should not be greater than Gratuity amount."))
            residual = self.termination_ids.residual
            if not residual:
                self.termination_ids.write({'fully_paid': True})
            self.termination_ids.write({'residual': residual})

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        termination_defaults = self.resolve_2many_commands('termination_ids', rec.get('termination_ids'))
        if termination_defaults and len(termination_defaults) == 1:
            termination = termination_defaults[0]
            partner_id = False
            employee_rec = self.env['hr.employee'].browse(termination['employee_id'][0])
            if termination['employee_id']:
                partner_id = employee_rec.address_home_id.id
                # if not slip.journal_id.default_debit_account_id:
                #     raise UserError(_('Please define Debit account for journal: %s') % (slip.journal_id.name))
                if not partner_id:
                    raise UserError(_('Please define Private Address for Employee: %s') % (employee_rec.name))
            currency_id = self.env.user.company_id.id
            rec['communication'] = 'Gratuity for '+ employee_rec.name
            rec['currency_id'] = currency_id
            rec['payment_type'] = 'outbound'
            rec['partner_type'] = 'supplier'
            rec['partner_id'] = partner_id
            rec['amount'] = termination['residual']
        return rec