# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mail_to_hr = fields.Char('HR Email')

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            mail_to_hr= self.env['ir.config_parameter'].sudo().get_param('hr_complete_solution.mail_to_hr'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('hr_complete_solution.mail_to_hr', self.mail_to_hr)