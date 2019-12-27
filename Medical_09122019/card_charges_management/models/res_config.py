# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from ast import literal_eval
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_bank_id = fields.Many2one('account.journal', 'Default Bank', domain=[('type', '=', 'bank')], required=True)
    default_card_id = fields.Many2one('account.journal', 'Default Card Journal', domain=[('type', '=', 'bank')], required=True)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        default_bank_id = literal_eval(ICPSudo.get_param('default_bank_id', default='False'))
        default_card_id = literal_eval(ICPSudo.get_param('default_card_id', default='False'))
        res.update({'default_bank_id': default_bank_id,
                    'default_card_id': default_card_id})
        return res

    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("default_bank_id", self.default_bank_id.id)
        ICPSudo.set_param("default_card_id", self.default_card_id.id)


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.constrains('default_bank_id', 'name')
    def _check_same_company_default_bank_id(self):
        if self.default_bank_id.company_id:
            if self.id != self.default_bank_id.company_id.id:
                raise ValidationError(_('Error ! Bank Journal should be of same company'))

    default_bank_id = fields.Many2one('account.journal', 'Default Bank', domain=[('type', '=', 'bank')], required=False)


    @api.constrains('default_card_id', 'name')
    def _check_same_company_default_card_id(self):
        if self.default_card_id.company_id:
            if self.id != self.default_card_id.company_id.id:
                raise ValidationError(_('Error ! Card Journal should be of same company'))

    default_card_id = fields.Many2one('account.journal', 'Default Card Journal', domain=[('type', '=', 'bank')],
                                      required=False)