# -*- coding: utf-8 -*-
from odoo import api, fields, models
from ast import literal_eval


class ChequeConfiguration(models.Model):
    _name = 'cheque.config.settings'
    _inherit = 'res.config.settings'

    email = fields.Char('Email', required=True)
    alert_inbound = fields.Integer('For Inbound Cheques', required=True, default=1)
    alert_outbound = fields.Integer('For Outbound Cheques', required=True, default=1)
    interim_account_id = fields.Many2one('account.account', string="Customer Cheque Interim Account", required=True)
    charges_account_id = fields.Many2one('account.account', string="Bank Charges Account", required=True)
    cheque_journal_p_id = fields.Many2one('account.journal', string="Cheque Payment Journal", required=True)
    cheque_journal_r_id = fields.Many2one('account.journal', string="Cheque Receive Journal", required=True)

    @api.model
    def get_values(self):
        res = super(ChequeConfiguration, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        email = ICPSudo.get_param('email')
        alert_inbound = literal_eval(ICPSudo.get_param('alert_inbound', default='False'))
        alert_outbound = literal_eval(ICPSudo.get_param('alert_outbound', default='False'))
        interim_account_id = literal_eval(ICPSudo.get_param('interim_account_id', default='False'))
        charges_account_id = literal_eval(ICPSudo.get_param('charges_account_id', default='False'))
        cheque_journal_p_id = literal_eval(ICPSudo.get_param('cheque_journal_p_id', default='False'))
        cheque_journal_r_id = literal_eval(ICPSudo.get_param('cheque_journal_r_id', default='False'))
        res.update({'email': email,
                    'alert_inbound': alert_inbound,
                    'alert_outbound': alert_outbound,
                    'interim_account_id': interim_account_id,
                    'charges_account_id': charges_account_id,
                    'cheque_journal_p_id': cheque_journal_p_id,
                    'cheque_journal_r_id': cheque_journal_r_id})
        return res

    @api.multi
    def set_values(self):
        res = super(ChequeConfiguration, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("email", self.email)
        ICPSudo.set_param("alert_inbound", self.alert_inbound)
        ICPSudo.set_param("alert_outbound", self.alert_outbound)
        ICPSudo.set_param("interim_account_id", self.interim_account_id.id)
        ICPSudo.set_param("charges_account_id", self.charges_account_id.id)
        ICPSudo.set_param("cheque_journal_p_id", self.cheque_journal_p_id.id)
        ICPSudo.set_param("cheque_journal_r_id", self.cheque_journal_r_id.id)
