# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sale_discount_total = fields.Boolean("Global discounts")

    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     return res
    #
    # @api.multi
    # def set_values(self):
    #     return super(ResConfigSettings, self).set_values()


