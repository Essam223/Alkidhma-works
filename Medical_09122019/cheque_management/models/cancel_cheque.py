# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from ast import literal_eval

class CancelCheque(models.TransientModel):
    _name = "cancel.cheque"

    comment = fields.Text(string="Comment", required=True)
    date_cancel = fields.Date(string='Cancel Date', default=fields.Date.context_today, required=True)

    @api.multi
    def cancel_cheque(self):
        cheque_obj = self.env['cheque.master'].browse(self.env.context.get('active_id'))
        for payment in cheque_obj.payment_ids:
            if payment.state == 'cancelled':
                continue
            print("CONTINUE SUCESS")
            Payment_reference = payment.name
            if cheque_obj.state == 'used':
                cheque_obj.write({'comment': self.comment+' '+ Payment_reference, 'state': 'cancelled'})
            else:
                ICPSudo = self.env['ir.config_parameter'].sudo()
                cheque_journal_p_id = literal_eval(ICPSudo.get_param('cheque_journal_p_id', default='False'))
                if not cheque_journal_p_id:
                    raise UserError(_('Set Cheque Payment Journal under Settings !!!'))
                cheque_journal_p_id = self.env['account.journal'].browse(cheque_journal_p_id)
                journal_id = cheque_journal_p_id.id
                account_id = cheque_journal_p_id.default_debit_account_id.id
                line_ids = [
                    (0, 0,
                     {'journal_id': journal_id, 'account_id':account_id,
                      'name': cheque_obj.name,
                      'amount_currency': 0.0, 'debit': cheque_obj.amount}),
                    (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.partner_account_id.id, 'name': '/',
                            'amount_currency': 0.0, 'credit': cheque_obj.amount, 'partner_id': cheque_obj.partner_id.id})
                ]

                vals = {
                    'journal_id': journal_id,
                    'ref': cheque_obj.name,
                    'date': self.date_cancel,
                    'line_ids': line_ids,
                }
                account_move = self.env['account.move'].create(vals)
                
                account_move.post()
                # raise UserError(_(str(account_move)))
                cheque_obj.write({'comment': self.comment+' '+ Payment_reference, 'cancel_date': self.date_cancel, 'state': 'cancelled','account_move_ids': [(4, account_move.id)],})
                # cheque_obj.cheque_ids.write({'state':'new'})
                payment.cancel()
                for record in cheque_obj.account_move_ids:
                    record.button_cancel()
                    record.unlink()


