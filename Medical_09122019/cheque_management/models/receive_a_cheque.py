# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from ast import literal_eval


class ReceiveACheque(models.TransientModel):
    _name = "receive.cheque2"

    name = fields.Char(string='Cheque No.', required=True)
    partner_type = fields.Selection([('customer', 'Customer'),
                                     ('supplier', 'Vendor')],
                                    'Partner Type',
                                    default='customer',
                                    required=True)
    partner_id = fields.Many2one('res.partner', string="Receiving From", required=True)
    partner_account_id = fields.Many2one('account.account', string="Partner Account", required=True)
    received_date = fields.Date(string='Receiving Date', required=True, default=fields.Date.context_today)
    cheque_date = fields.Date(string='Cheque Date', required=True, default=fields.Date.context_today)
    bank_name = fields.Many2one('customer.bank', string='Customer Bank Name', required=True)
    amount = fields.Float('Amount', required=True)

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_type == 'customer':
            self.partner_account_id = self.partner_id.property_account_receivable_id
        elif self.partner_type == 'supplier':
            self.partner_account_id = self.partner_id.property_account_payable_id
        else:
            pass

    @api.multi
    def receive_cheque(self):
        if self.amount <= 0:
            raise UserError(_('Cheque amount must be greater than zero !!!'))
        cheque_master = self.env['receive.cheque.master']
        search_ids = cheque_master.search([('name', '=', self.name),
                                           ('partner_id', '=', self.partner_id.id),
                                           ('bank_name', '=', self.bank_name.id)])
        if search_ids:
            raise UserError(_('Cheque with same details already Received. Please check given details !!!'))

        ICPSudo = self.env['ir.config_parameter'].sudo()
        cheque_journal_r_id = literal_eval(ICPSudo.get_param('cheque_journal_r_id', default='False'))
        if not cheque_journal_r_id:
            raise UserError(_('Set Cheque Receipt Journal under Settings !!!'))
        journal_id = cheque_journal_r_id
        cheque_journal_r_id = self.env['account.journal'].browse(cheque_journal_r_id)
        partner_account_id = self.partner_account_id
        if not partner_account_id:
            if self.partner_type == 'customer':
                partner_account_id = self.partner_id.property_account_receivable_id
            elif self.partner_type == 'supplier':
                partner_account_id = self.partner_id.property_account_payable_id
            else:
                partner_account_id = self.partner_id.property_account_receivable_id
        vals = {
            'name': self.name,
            'partner_type': self.partner_type,
            'partner_id': self.partner_id.id,
            'partner_account_id': partner_account_id.id,
            'received_date': self.received_date,
            'cheque_date': self.cheque_date,
            'amount': self.amount,
            'bank_name': self.bank_name.id,
            'state': 'received',
        }
        cheque_id = cheque_master.create(vals)
        payment_type = 'inbound'
        payment_methods = cheque_journal_r_id.inbound_payment_method_ids or cheque_journal_r_id.outbound_payment_method_ids
        payment_method_id = payment_methods and payment_methods[0] or False
        values = {
            'payment_type': payment_type,
            'partner_type': self.partner_type,
            'communication': self.name,
            'is_cheque': True,
            'partner_id': self.partner_id.id,
            'amount': self.amount,
            'payment_date': self.received_date,
            'journal_id': journal_id,
            'payment_method_id': payment_method_id.id,
            'receive_cheque_id': cheque_id.id
        }
        account_payment = self.env['account.payment'].create(values)
        account_payment.post()



    @api.multi
    def action_clear(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Receive A Cheque',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'receive.cheque2',
            'target': 'new',
            'context': 'None'
        }
