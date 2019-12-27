# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from ast import literal_eval


class IssueCheque(models.Model):
    _name = "issue.cheque"

    cheque_id = fields.Many2one('cheque.master', string='Cheque Number', domain="[('state', 'in', ['new','reuse'])]", required=True)
    date_issue = fields.Date(string='Print Date', default=fields.Date.context_today, required=True)
    cheque_date = fields.Date(string='Cheque Date', required=True)
    partner_id = fields.Many2one('res.partner', string="Issued To", required=True)
    name_in_cheque = fields.Char(string="Name in Cheque", required=True)
    issue_journal_entry = fields.Many2one('account.move', 'Accounting Entry', readonly=True)
    dest_account_id = fields.Many2one('account.account', string="Destination Account", required=True)
    amount = fields.Float('Amount', required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('used', 'Used'),
        ('printed', 'Printed'),
    ], string='Status', readonly=True, default='new')

    @api.multi
    def copy(self):
        raise UserError(_('You cannot duplicate this record.'))

    @api.onchange('date_issue')
    def _onchange_date_issue(self):
        if self.date_issue and not self.cheque_date:
            self.cheque_date = self.date_issue

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id:
            self.name_in_cheque = self.partner_id.name
        if self.partner_id.supplier:
            self.dest_account_id = self.partner_id.property_account_payable_id
        elif self.partner_id.customer:
            self.dest_account_id = self.partner_id.property_account_receivable_id
        else:
            pass

    @api.model
    def create(self, vals):
        if vals['amount'] <= 0:
            raise UserError(_('Cheque amount must be greater than zero !!!'))
        self.env['cheque.master'].browse(vals['cheque_id']).write({'state': 'used',
                                                                   'partner_id': vals['partner_id'],
                                                                   'partner_account_id': vals['dest_account_id'],
                                                                   'date_issue': vals['date_issue'],
                                                                   'cheque_date': vals['cheque_date'],
                                                                   })
        vals['state'] = 'used'
        return super(IssueCheque, self).create(vals)

    @api.multi
    def post_cheque(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        cheque_journal_p_id = literal_eval(ICPSudo.get_param('cheque_journal_p_id', default='False'))
        if not cheque_journal_p_id:
            raise UserError(_('Set Cheque Payment Journal under Settings !!!'))
        cheque_journal_p_id = self.env['account.journal'].browse(cheque_journal_p_id)
        journal_id = cheque_journal_p_id.id
        payment_type = 'outbound'
        payment_methods = cheque_journal_p_id.inbound_payment_method_ids or cheque_journal_p_id.outbound_payment_method_ids
        payment_method_id = payment_methods and payment_methods[0] or False
        values = {
            'payment_type': payment_type,
            'partner_type': 'supplier',
            'communication': self.cheque_id.name,
            'is_cheque': True,
            'partner_id': self.partner_id.id,
            'amount': self.amount,
            'payment_date': self.date_issue,
            'journal_id': journal_id,
            'payment_method_id': payment_method_id.id,
            'cheque_id': self.cheque_id.id
        }
        account_payment = self.env['account.payment'].create(values)
        account_payment.post()
        self.state = 'printed'
        self.cheque_id.write({'state': 'printed',
                              'date_issue': self.date_issue,
                              'cheque_date': self.cheque_date,
                              # 'account_move_ids': [(4, account_move.id)],
                              'partner_id': self.partner_id.id,
                              'partner_account_id': self.dest_account_id.id,
                              'amount': self.amount})

    # @api.multi
    # def print_cheque(self):
    #     print "printttt_chequeeeeee"
