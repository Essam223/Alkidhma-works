# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
import datetime
from odoo.osv import expression
from datetime import timedelta, date


class CustomBank(models.Model):
    _inherit = 'res.bank'

    bank_code = fields.Char(string='Short Name', required=True)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        # args = args or []
        args = []
        domain = []
        if name:
            domain = ['|', ('bic', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&'] + domain
        banks = self.search(domain + args, limit=limit)
        return banks.name_get()


class CompanyBankAccount(models.Model):
    _name = 'company.bank.account'
    _rec_name = 'bank_account_id'

    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    bank_account_id = fields.Many2one('res.partner.bank', 'Bank Acc No', required=True,
                                      # domain="[('partner_id', '=', partner_id)]",
                                      help='Company Bank Account')

    bank_id = fields.Many2one('res.bank', related='bank_account_id.bank_id', string="Bank", copy=False)
    bank_code = fields.Char(related='bank_id.bank_code', string='Short Name')
    iban_code = fields.Char(string='IBAN Code', required=True)


class ResCompany(models.Model):
    _inherit = 'res.company'

    Employer_EID = fields.Char('Employer EID', required=True)
    Payer_EID = fields.Char('Payer EID', required=True)
    Payer_QID = fields.Char('Payer QID')

    bank_account_ids = fields.One2many('company.bank.account', 'company_id', string='Bank Account')


