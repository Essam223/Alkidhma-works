# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from ast import literal_eval
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    email = fields.Char('Email')
    alert_inbound = fields.Integer('For Inbound Cheques', default=1)
    alert_outbound = fields.Integer('For Outbound Cheques', default=1)
    interim_account_id = fields.Many2one('account.account', string="Customer Cheque Interim Account")
    charges_account_id = fields.Many2one('account.account', string="Bank Charges Account")
    cheque_journal_p_id = fields.Many2one('account.journal', string="Cheque Payment Journal")
    cheque_journal_r_id = fields.Many2one('account.journal', string="Cheque Receive Journal")

    @api.constrains('interim_account_id', 'charges_account_id', 'cheque_journal_p_id', 'cheque_journal_r_id', 'name')
    def _check_same_company_account(self):
        if self.interim_account_id.company_id:
            if self.id != self.interim_account_id.company_id.id:
                raise ValidationError(_('Error ! Customer Cheque Interim Account should be of same company'))
        if self.charges_account_id.company_id:
            if self.id != self.charges_account_id.company_id.id:
                raise ValidationError(_('Error ! Bank Charges Account should be of same company'))
        if self.cheque_journal_p_id.company_id:
            if self.id != self.cheque_journal_p_id.company_id.id:
                raise ValidationError(_('Error ! Cheque Payment Journal should be of same company'))
        if self.cheque_journal_r_id.company_id:
            if self.id != self.cheque_journal_r_id.company_id.id:
                raise ValidationError(_('Error ! Cheque Receive Journal should be of same company'))