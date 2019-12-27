# -*- coding: utf-8 -*-
from odoo import fields, models, api
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _getExpenseId(self):
        return [('user_type_id', '=', self.env.ref('account.data_account_type_expenses').id),
                ('deprecated', '=', False)]

    default_discount_account = fields.Many2one('account.account', string='Invoice Discount Account',
                                       domain=_getExpenseId,
                                       help="The discount account used for this invoice.")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        default_discount_account = literal_eval(ICPSudo.get_param('default_discount_account', default='False'))
        res.update({'default_discount_account': default_discount_account})
        return res

    @api.multi
    def set_values(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSettings, self).set_values()
        ICPSudo.set_param("default_discount_account", self.default_discount_account.id)