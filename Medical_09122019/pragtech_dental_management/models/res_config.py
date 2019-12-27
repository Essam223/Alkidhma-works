# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _getIncomeId(self):
        return [('user_type_id', '=', self.env.ref('account.data_account_type_revenue').id),
                ('deprecated', '=', False)]

    default_insurance_diff_account = fields.Many2one('account.account', string='Insurance difference Account',
                                       domain=_getIncomeId,
                                       help="The Insurance difference account used for this invoice.")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        default_insurance_diff_account = literal_eval(ICPSudo.get_param('default_insurance_diff_account', default='False'))
        res.update({'default_insurance_diff_account': default_insurance_diff_account})
        return res

    @api.multi
    def set_values(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSettings, self).set_values()
        ICPSudo.set_param("default_insurance_diff_account", self.default_insurance_diff_account.id)


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.constrains('default_insurance_diff_account', 'name')
    def _check_same_company_insurance_diff_account(self):
        if self.default_insurance_diff_account.company_id:
            if self.id != self.default_insurance_diff_account.company_id.id:
                raise ValidationError(_('Error ! Insurance difference Account should be of same company'))

    def _getIncomeId(self):
        return [('user_type_id', '=', self.env.ref('account.data_account_type_revenue').id),
                ('deprecated', '=', False)]

    default_insurance_diff_account = fields.Many2one('account.account', string='Insurance difference Account',
                                       domain=_getIncomeId,
                                       help="The Insurance difference account used for this invoice.")

    @api.constrains('default_discount_account', 'name')
    def _check_same_company_discount_account(self):
        if self.default_discount_account.company_id:
            if self.id != self.default_discount_account.company_id.id:
                raise ValidationError(_('Error ! Discount Account should be of same company'))

    def _getExpenseId(self):
        return [('user_type_id', '=', self.env.ref('account.data_account_type_expenses').id),
                ('deprecated', '=', False)]

    default_discount_account = fields.Many2one('account.account', string='Invoice Discount Account',
                                               domain=_getExpenseId,
                                               help="The discount account used for this invoice.")