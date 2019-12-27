# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from ast import literal_eval


class ReturnCheque(models.TransientModel):
    _name = "return.cheque"

    date_present = fields.Date(string='Cheque Present Date', default=fields.Date.context_today, required=True)
    date_return = fields.Date(string='Cheque Return Date', default=fields.Date.context_today, required=True)
    amount = fields.Float('Bank Charges', required=True)
    reason_id = fields.Many2one('return.reason', string='Reason', required=True)
    comment_required = fields.Boolean(string="Comment Required ?")
    comment = fields.Text(string="Comment")

    @api.onchange('reason_id')
    def _onchange_reason(self):
        if self.reason_id:
            self.comment_required = self.reason_id.comment_required

    @api.multi
    def return_cheque(self):
        cheque_obj = self.env['cheque.master'].browse(self.env.context.get('active_id'))
        ICPSudo = self.env['ir.config_parameter'].sudo()
        cheque_journal_p_id = literal_eval(ICPSudo.get_param('cheque_journal_p_id', default='False'))
        if not cheque_journal_p_id:
            raise UserError(_('Set Cheque Payment Journal under Settings !!!'))
        cheque_journal_p_id = self.env['account.journal'].browse(cheque_journal_p_id)
        journal_id = cheque_journal_p_id.id
        line_ids = []
        if self.amount and self.amount > 0:
            line_ids = [(0, 0,
             {'journal_id': journal_id, 'account_id': cheque_obj.bank_name.account_id.id, 'name': '/',
              'amount_currency': 0.0, 'credit': self.amount}),
            (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.bank_name.return_account_id.id,
                    'name': 'Bank Charges', 'partner_id': cheque_obj.partner_id.id, 'amount_currency': 0.0, 'debit': self.amount}),]
        line_ids.extend([
            (0, 0,
             {'journal_id': journal_id, 'account_id': cheque_obj.partner_account_id.id, 'name': '/',
              'amount_currency': 0.0, 'credit': cheque_obj.amount}),
            (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.bank_name.account_id.id,
                    'name': cheque_obj.name, 'amount_currency': 0.0, 'debit': cheque_obj.amount}),
            (0, 0,
             {'journal_id': journal_id, 'account_id': cheque_obj.bank_name.account_id.id, 'name': '/',
              'amount_currency': 0.0, 'credit': cheque_obj.amount}),
            (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.bank_name.pdc_account_id.id,
                    'name': cheque_obj.name, 'amount_currency': 0.0, 'debit': cheque_obj.amount})
        ])
        vals = {
            'journal_id': journal_id,
            'ref': cheque_obj.name,
            'date': self.date_return,
            'line_ids': line_ids,
        }
        account_move = self.env['account.move'].create(vals)
        account_move.post()
        if cheque_obj.comment:
            comment = cheque_obj.comment + "\n" + self.reason_id.name
        else:
            comment = self.reason_id.name
        if self.comment:
            comment = comment + "\n" + self.comment
        cheque_obj.write({'state': 'returned', 'return_date': self.date_return, 'comment': comment,'account_move_ids': [(4, account_move.id)],})
