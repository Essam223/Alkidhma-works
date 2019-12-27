# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from ast import literal_eval


class DishonourCheque(models.TransientModel):
    _name = "dishonour.cheque"

    present_date = fields.Date(string='Cheque Present Date', default=fields.Date.context_today, required=True)
    date_return = fields.Date(string='Cheque Return Date', default=fields.Date.context_today, required=True)
    charge = fields.Float('Service Charges if any')

    @api.multi
    def dishonour_cheque(self):
        cheque_obj = self.env['receive.cheque.master'].browse(self.env.context.get('active_id'))
        ICPSudo = self.env['ir.config_parameter'].sudo()
        cheque_journal_r_id = literal_eval(ICPSudo.get_param('cheque_journal_r_id', default='False'))
        if not cheque_journal_r_id:
            raise UserError(_('Set Cheque Receipt Journal under Settings !!!'))
        journal_id = cheque_journal_r_id
        cheque_journal_r_id = self.env['account.journal'].browse(cheque_journal_r_id)
        ICPSudo = self.env['ir.config_parameter'].sudo()
        charges_account_id = literal_eval(ICPSudo.get_param('charges_account_id', default='False'))
        line_ids = []
        if self.charge and self.charge > 0:
            line_ids = [(0, 0,
                         {'journal_id': journal_id, 'account_id': cheque_obj.bank_id.account_id.id, 'name': '/',
                            'amount_currency': 0.0, 'credit': self.charge}),
                        (0, 0, {'journal_id': journal_id, 'account_id': charges_account_id,
                                'partner_id': cheque_obj.partner_id.id,
                                'name': 'Bank Charges', 'amount_currency': 0.0, 'debit': self.charge})]
        line_ids.extend([(0, 0,
                          {'journal_id': journal_id, 'account_id': cheque_obj.bank_id.account_id.id, 'name': '/',
                           'amount_currency': 0.0, 'credit': cheque_obj.amount}),
                         (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.partner_account_id.id,
                                 'partner_id': cheque_obj.partner_id.id,
                                 'name': cheque_obj.name, 'amount_currency': 0.0, 'debit': cheque_obj.amount}),

                         (0, 0,
                          {'journal_id': journal_id, 'account_id': cheque_journal_r_id.default_credit_account_id.id, 'name': '/',
                           'partner_id': cheque_obj.partner_id.id,
                           'amount_currency': 0.0, 'credit': cheque_obj.amount}),
                         (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.bank_id.account_id.id,
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
        cheque_obj.write({'state': 'dishonoured',
                          'present_date': self.present_date,
                          'date_return': self.date_return,
                          'account_move_ids': [(4, account_move.id)],})
