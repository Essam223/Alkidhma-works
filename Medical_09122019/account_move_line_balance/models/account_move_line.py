# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    date = fields.Datetime(required=True, states={'posted': [('readonly', True)]}, index=True,
                           default=fields.Date.context_today)

    # @api.multi
    # def post(self):
    #     invoice = self._context.get('invoice', False)
    #     self._post_validate()
    #     for move in self:
    #         move.line_ids.create_analytic_lines()
    #         if move.name == '/':
    #             new_name = False
    #             journal = move.journal_id
    #
    #             if invoice and invoice.move_name and invoice.move_name != '/':
    #                 new_name = invoice.move_name
    #             else:
    #                 if journal.sequence_id:
    #                     # If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
    #                     sequence = journal.sequence_id
    #                     if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
    #                         if not journal.refund_sequence_id:
    #                             raise UserError(_('Please define a sequence for the credit notes'))
    #                         sequence = journal.refund_sequence_id
    #                     from datetime import datetime
    #                     date_here = datetime.strptime(move.date, '%Y-%m-%d %H:%M:%S')
    #                     new_name = sequence.with_context(ir_sequence_date=str(date_here.date())).next_by_id()
    #                 else:
    #                     raise UserError(_('Please define a sequence on the journal.'))
    #
    #             if new_name:
    #                 move.name = new_name
    #     return self.write({'state': 'posted'})


class ResCompany(models.Model):
    _inherit = "res.company"

    account_opening_date = fields.Datetime(string='Opening Date', related='account_opening_move_id.date',
                                           help="Date at which the opening entry of this company's accounting "
                                                "has been posted.")


class FinancialYearOpeningWizard(models.TransientModel):
    _inherit = 'account.financial.year.op'

    opening_date = fields.Datetime(string='Opening Date', required=True, related='company_id.account_opening_date',
                               help="Date from which the accounting is managed in Odoo. It is the date of the opening"
                                    " entry.")


class OpeningAccountMoveWizard(models.TransientModel):
    _inherit = 'account.opening'

    date = fields.Datetime(string='Opening Date', required=True, related='opening_move_id.date')


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    date = fields.Datetime(related='move_id.date', string='Date', index=True, store=True, copy=False)
    # related is required

    def _get_balance_after_trans(self):
        for a_m_l in self:
            prev_move_line = self.env['account.move.line'].search([('account_id', '=', a_m_l.account_id.id),
                                                                   ('date', '<', a_m_l.date),
                                                                   ('move_id.state', '=', 'posted'),
                                                                   ])
            curr_id_move_line = self.env['account.move.line'].search([('account_id', '=', a_m_l.account_id.id),
                                                                   ('date', '=', a_m_l.date),
                                                                   ('id', '=', a_m_l.id),
                                                                   ('move_id.state', '=', 'posted'),
                                                                   ])
            curr_date_id_prev_m_l = self.env['account.move.line'].search([('account_id', '=', a_m_l.account_id.id),
                                                                   ('date', '=', a_m_l.date),
                                                                   ('id', '<', a_m_l.id),
                                                                   ('move_id.state', '=', 'posted'),
                                                                   ])
            total_debit = 0.0
            total_credit = 0.0
            for move_line in prev_move_line + curr_id_move_line + curr_date_id_prev_m_l:
                total_debit = total_debit + move_line.debit
                total_credit = total_credit + move_line.credit

            a_m_l.balance_after_trans = total_debit - total_credit

    balance_after_trans = fields.Monetary(string='Balance', readonly=True, compute='_get_balance_after_trans')