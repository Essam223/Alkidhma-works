# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class DepositCheque(models.TransientModel):
    _name = "deposit.cheque"

    deposit_date = fields.Date(string='Date of Deposit', default=fields.Date.context_today, required=True)
    bank_id = fields.Many2one('account.bank', string='Bank Name', required=True)

    @api.multi
    def deposit_cheque(self):
        cheque_obj = self.env['receive.cheque.master'].browse(self.env.context.get('active_id'))
        cheque_obj.write({'state': 'deposited', 'deposit_date': self.deposit_date, 'bank_id': self.bank_id.id})
