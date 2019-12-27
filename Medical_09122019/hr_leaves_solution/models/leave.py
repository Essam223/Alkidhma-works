# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'
    _description = "Holidays"

    expected_rejoining_date = fields.Datetime(string="Expected rejoining date", readonly=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, track_visibility='onchange')
    actual_rejoining_date = fields.Datetime(string="Actual rejoining date", track_visibility='onchange')

    edit_by_hr = fields.Boolean(compute='_compute_can_edit_name')

    def _compute_can_edit_name(self):
        for rec in self:
            edit_only_by_hr = False
            group_hr_holidays_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
            group_hr_holidays_user = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
            if not group_hr_holidays_manager or not group_hr_holidays_user:
                edit_only_by_hr = False
            if group_hr_holidays_manager or group_hr_holidays_user:
                if rec.state in ('draft', 'confirm'):
                    edit_only_by_hr = True
            rec.edit_by_hr = edit_only_by_hr

    allocation_date = fields.Date(default=fields.Date.today, help="Leave allocated date", track_visibility='onchange')
    allocation_range = fields.Selection([('year', 'Yearly'), ('month', 'Monthly')],
                                        'Leave frequency',
                                        help="Periodicity on which you want automatic allocation of leaves to "
                                             "eligible employees.", track_visibility='onchange')

    @api.onchange('date_to')
    def _onchange_date_to(self):
        """ Update Expected rejoining date. """
        res = super(HrHolidays, self)._onchange_date_to()
        self.expected_rejoining_date = self.date_to

    holidays_ext_id = fields.Many2one('hr.holidays', string='Extended from leave')
    extended_ids = fields.One2many('hr.holidays', 'holidays_ext_id', string='Extended Leaves')

    is_carry_forward_leave = fields.Boolean('Carry forward', track_visibility='onchange')
    date_carry_forward = fields.Date('Leave Expiry Date', track_visibility='onchange')

    @api.onchange('holiday_status_id')
    def _onchange_holiday_status_id(self):
        self.is_carry_forward_leave = self.holiday_status_id.is_carry_forward_leave
