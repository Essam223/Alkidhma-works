# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class ReceiveCheque(models.TransientModel):
    _name = "receive.cheque"

    bank_name = fields.Many2one('account.bank', string='Bank Name', required=True)
    cheque_from = fields.Integer(string='From', required=True)
    cheque_to = fields.Integer(string='To', required=True)

    # @api.onchange('cheque_from', 'cheque_to')
    # def _onchange_cheque_no(self):
    #     if self.cheque_from > self.cheque_to:
    #         raise UserError(_('Reset Cheque Number From and To properly.'))

    @api.multi
    def receive_cheque(self):
        if self.cheque_from > self.cheque_to:
            raise UserError(_('Reset Cheque Number From and To properly.'))
        bank_name = self.bank_name
        cheque_from = self.cheque_from
        cheque_to = self.cheque_to
        cheque_obj = self.env['cheque.master']
        for x in range(cheque_from, cheque_to+1):
            name = '[' + str(x) + '] ' + bank_name.name
            similar_cheques = cheque_obj.search([('name', '=', name)])
            if similar_cheques:
                raise UserError(_('Cheque with given details already exists. Reset Cheque Number properly.'))
        for x in range(cheque_from, cheque_to+1):
            name = '[' + str(x) + '] ' + bank_name.name
            vals = {
                'name': name,
                'cheque_no': x,
                'bank_name': bank_name.id,
                'state': 'new'
                    }
            cheque_obj.create(vals)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cheque Master Book',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'cheque.master',
            'context': 'None'
        }

    @api.multi
    def action_clear(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Receive Cheque',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'receive.cheque',
            'target': 'new',
            'context': 'None'
        }
