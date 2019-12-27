# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import time


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    auto_allocation = fields.Boolean('Auto renewal')
    allocation_range = fields.Selection([('year', 'Yearly'), ('month', 'Monthly')],
                                        'Leave frequency', default='year',
                                        help="Periodicity on which you want automatic allocation of leaves to "
                                             "eligible employees.")
    days_to_allocate = fields.Float('Days to Allocate',
                                    help="In automatic allocation of leaves, given days will be allocated every period.")

    is_carry_forward_leave = fields.Boolean('Carry forward', default=True)
