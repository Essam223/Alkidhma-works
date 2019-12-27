# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    overtime_hourly_rate_holiday = fields.Float('Overtime Hourly rate(Holiday)')
    overtime_hourly_rate_working_day = fields.Float('Overtime Hourly rate(Working day)')

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            overtime_hourly_rate_holiday= float(self.env['ir.config_parameter'].sudo().get_param('hr_attendance_overtime.overtime_hourly_rate_holiday')),
            overtime_hourly_rate_working_day= float(self.env['ir.config_parameter'].sudo().get_param('hr_attendance_overtime.overtime_hourly_rate_working_day')),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('hr_attendance_overtime.overtime_hourly_rate_holiday', self.overtime_hourly_rate_holiday)
        self.env['ir.config_parameter'].sudo().set_param('hr_attendance_overtime.overtime_hourly_rate_working_day', self.overtime_hourly_rate_working_day)