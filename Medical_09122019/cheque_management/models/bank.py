# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountBank(models.Model):
    _name = "account.bank"

    name = fields.Char(string='Bank Name', required=True)
    account_id = fields.Many2one('account.account', string="Account", required=True)
    pdc_account_id = fields.Many2one('account.account', string="PDC Interim Account", required=True)
    return_account_id = fields.Many2one('account.account', string="Return Charges Account", required=True,
                    domain=lambda self: [('user_type_id', '=', self.env.ref('account.data_account_type_expenses').id)])
    account_no = fields.Char(string='Account Number', required=True)
    _sql_constraints = [('name_uniq', 'unique (name)', 'The name of the bank must be unique !')]
