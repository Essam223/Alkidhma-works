# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from ast import literal_eval


class ClearCheque(models.TransientModel):
    _name = "clear.cheque"

    date_clear = fields.Date(string='Clear Date', default=fields.Date.context_today, required=True)

    @api.multi
    def immediate_clear_cheque(self):
        cheques = self.env['cheque.master'].browse(self.env.context.get('active_ids'))
        for cheque_obj in cheques:
            if cheque_obj.state not in ('issued','pending'):
                raise UserError('You can clear only cheques in Issued or Pending status !!!')
        ICPSudo = self.env['ir.config_parameter'].sudo()
        cheque_journal_p_id = literal_eval(ICPSudo.get_param('cheque_journal_p_id', default='False'))
        if not cheque_journal_p_id:
            raise UserError(_('Set Cheque Payment Journal under Settings !!!'))
        journal_id = cheque_journal_p_id
        for cheque_obj in cheques:
            line_ids = [
                (0, 0,
                 {'journal_id': journal_id, 'account_id': cheque_obj.bank_name.account_id.id, 'name': '/',
                  'amount_currency': 0.0, 'credit': cheque_obj.amount}),
                (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.bank_name.pdc_account_id.id,
                        'partner_id': cheque_obj.partner_id.id,
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
    def hold_cheque(self):
        cheque_obj = self.env['cheque.master'].browse(self.env.context.get('active_id'))
        today = fields.Date.context_today(self)
        if self.date_clear < today:
            raise UserError('Hold date must not be less than today. Reset Hold date !!!')

        else:
            cheque_obj.write({'hold_date': self.date_clear, 'state': 'hold'})

    @api.multi
    def hold_receive_cheque(self):
        cheque_obj = self.env['receive.cheque.master'].browse(self.env.context.get('active_id'))
        today = fields.Date.context_today(self)
        if self.date_clear < today:
            raise UserError('Hold date must not be less than today. Reset Hold date !!!')

        else:
            cheque_obj.write({'hold_date': self.date_clear, 'state': 'hold'})

    @api.multi
    def clear_cheque(self):
        cheque_obj = self.env['cheque.master'].browse(self.env.context.get('active_id'))
        ICPSudo = self.env['ir.config_parameter'].sudo()
        cheque_journal_p_id = literal_eval(ICPSudo.get_param('cheque_journal_p_id', default='False'))
        if not cheque_journal_p_id:
            raise UserError(_('Set Cheque Payment Journal under Settings !!!'))
        journal_id = cheque_journal_p_id
        line_ids = [
            (0, 0,
             {'journal_id': journal_id, 'account_id': cheque_obj.bank_name.account_id.id, 'name': '/',
              'amount_currency': 0.0, 'credit': cheque_obj.amount}),
            (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.bank_name.pdc_account_id.id, 'partner_id': cheque_obj.partner_id.id,
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
