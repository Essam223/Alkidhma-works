# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from ast import literal_eval


class ReceiveClearCheque(models.TransientModel):
    _name = "receive.clear.cheque"

    date_clear = fields.Date(string='Clear Date', default=fields.Date.context_today, required=True)

    @api.multi
    def immediate_receive_clear_cheque(self):
        cheques = self.env['receive.cheque.master'].browse(self.env.context.get('active_ids'))
        for cheque_obj in cheques:
            if cheque_obj.state != 'deposited':
                raise UserError('You can clear only cheques already deposited !!!')
        ICPSudo = self.env['ir.config_parameter'].sudo()
        cheque_journal_r_id = literal_eval(ICPSudo.get_param('cheque_journal_r_id', default='False'))
        if not cheque_journal_r_id:
            raise UserError(_('Set Cheque Receipt Journal under Settings !!!'))
        cheque_journal_r_id = self.env['account.journal'].browse(cheque_journal_r_id)
        journal_id = cheque_journal_r_id.id
        ICPSudo = self.env['ir.config_parameter'].sudo()
        interim_account_id = literal_eval(ICPSudo.get_param('interim_account_id', default='False'))
        if not interim_account_id:
            raise UserError(_('Set Customer Cheque Interim Account under Settings !!!'))
        for cheque_obj in cheques:
            line_ids = [
                (0, 0,
                 {'journal_id': journal_id, 'account_id': interim_account_id, 'name': '/',
                  'partner_id': cheque_obj.partner_id.id,
                  'amount_currency': 0.0, 'credit': cheque_obj.amount}),
                (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.bank_id.account_id.id,
                        'name': cheque_obj.name + ' Clearance', 'amount_currency': 0.0, 'debit': cheque_obj.amount})
            ]
            vals = {
                'journal_id': journal_id,
                'ref': cheque_obj.name,
                'date': self.date_clear,
                'line_ids': line_ids,
            }
            account_move = self.env['account.move'].create(vals)
            account_move.post()
            cheque_obj.write(
                {'state': 'cleared', 'clear_date': self.date_clear, 'account_move_ids': [(4, account_move.id)], })

    @api.multi
    def receive_clear_cheque(self):
        cheque_obj = self.env['receive.cheque.master'].browse(self.env.context.get('active_id'))
        ICPSudo = self.env['ir.config_parameter'].sudo()
        cheque_journal_r_id = literal_eval(ICPSudo.get_param('cheque_journal_r_id', default='False'))
        if not cheque_journal_r_id:
            raise UserError(_('Set Cheque Receipt Journal under Settings !!!'))
        cheque_journal_r_id = self.env['account.journal'].browse(cheque_journal_r_id)
        journal_id = cheque_journal_r_id.id
        account = cheque_journal_r_id.default_credit_account_id
        line_ids = [
            (0, 0,
             {'journal_id': journal_id, 'account_id': account.id, 'name': '/',
              'partner_id': cheque_obj.partner_id.id,
              'amount_currency': 0.0, 'credit': cheque_obj.amount}),
            (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.bank_id.account_id.id,
                    'name': cheque_obj.name + ' Clearance', 'amount_currency': 0.0, 'debit': cheque_obj.amount})
        ]
        vals = {
            'journal_id': journal_id,
            'ref': cheque_obj.name,
            'date': self.date_clear,
            'line_ids': line_ids,
        }
        account_move = self.env['account.move'].create(vals)
        account_move.post()
        cheque_obj.write({'state': 'cleared', 'clear_date': self.date_clear, 'account_move_ids': [(4, account_move.id)],})
