# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2004-2008 PC Solutions (<http://pcsol.be>). All Rights Reserved
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_cheque = fields.Boolean('Is Cheque?', default=False)
    cheque_name = fields.Char(string='Cheque No.')
    cheque_id = fields.Many2one('cheque.master', 'Outbound Cheque')
    receive_cheque_id = fields.Many2one('receive.cheque.master', 'Inbound Cheque')
    received_date = fields.Date(string='Receiving Date', default=fields.Date.context_today)
    cheque_date = fields.Date(string='Cheque Date', default=fields.Date.context_today)
    bank_name = fields.Many2one('customer.bank', string='Customer Bank Name')

    cheque_id = fields.Many2one('cheque.master', string='Cheque Number', domain="[('state', '=', 'new')]")
    date_issue = fields.Date(string='Print Date', default=fields.Date.context_today)
    name_in_cheque = fields.Char(string="Name in Cheque")

    @api.onchange('cheque_id')
    def onchange_cheque_id(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        cheque_journal_p_id = literal_eval(ICPSudo.get_param('cheque_journal_p_id', default='False'))
        if self.is_cheque:
            self.journal_id = cheque_journal_p_id

    def action_validate_invoice_payment(self):
        """ Posts a payment used to pay an invoice. This function only posts the
        payment by default but can be overridden to apply specific post or pre-processing.
        It is called by the "validate" button of the popup window
        triggered on invoice form by the "Register Payment" button.
        """
        if any(len(record.invoice_ids) != 1 for record in self):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(_("This method should only be called to process a single invoice's payment."))
        if self.is_cheque and self.payment_type == 'inbound':
            active_ids = self._context.get('active_ids')
            if self.amount <= 0:
                raise UserError(_('Cheque amount must be greater than zero !!!'))
            cheque_master = self.env['receive.cheque.master']
            search_ids = cheque_master.search([('name', '=', self.cheque_name),
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
            partner_account_id = False
            if self.partner_type == 'customer':
                partner_account_id = self.partner_id.property_account_receivable_id
            elif self.partner_type == 'supplier':
                partner_account_id = self.partner_id.property_account_payable_id
            vals = {
                'name': self.cheque_name,
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
            invoices = self.env['account.invoice'].browse(active_ids)
            values = {
                'payment_type': payment_type,
                'partner_type': self.partner_type,
                'communication': self.cheque_name,
                'is_cheque': True,
                'partner_id': self.partner_id.id,
                'amount': self.amount,
                'payment_date': self.received_date,
                'journal_id': journal_id,
                'payment_method_id': payment_method_id.id,
                'receive_cheque_id': cheque_id.id,
                'invoice_ids': [(6, 0, invoices.ids)],
            }
            self.write(values)
            self.post()
        elif self.is_cheque and self.payment_type == 'outbound':
            active_ids = self._context.get('active_ids')
            ICPSudo = self.env['ir.config_parameter'].sudo()
            cheque_journal_p_id = literal_eval(ICPSudo.get_param('cheque_journal_p_id', default='False'))
            if not cheque_journal_p_id:
                raise UserError(_('Set Cheque Payment Journal under Settings !!!'))
            journal_id = cheque_journal_p_id
            cheque_journal_p_id = self.env['account.journal'].browse(cheque_journal_p_id)
            payment_type = 'outbound'
            payment_methods = self.payment_type == 'inbound' and cheque_journal_p_id.inbound_payment_method_ids or cheque_journal_p_id.outbound_payment_method_ids
            payment_method_id = payment_methods and payment_methods[0] or False
            invoices = self.env['account.invoice'].browse(active_ids)
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
                'cheque_id': self.cheque_id.id,
                'invoice_ids': [(6, 0, invoices.ids)],
            }
            self.write(values)
            self.post()
            dest_account_id = False
            if self.partner_type == 'supplier':
                dest_account_id = self.partner_id.property_account_payable_id
            elif self.partner_type == 'customer':
                dest_account_id = self.partner_id.property_account_receivable_id
            self.cheque_id.write({'state': 'printed',
                                  'date_issue': self.date_issue,
                                  'cheque_date': self.cheque_date,
                                  'partner_id': self.partner_id.id,
                                  'partner_account_id': dest_account_id.id,
                                  'amount': self.amount})
        else:
            return self.post()
