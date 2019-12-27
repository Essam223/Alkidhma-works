# -*- coding: utf-8 -*-
import datetime, time
from dateutil import relativedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class HrContract(models.Model):
    _inherit = 'hr.contract'

    wage = fields.Monetary('Basic Salary', digits=(16, 2), required=True, help="Employee's monthly gross Basic Salary.")
    accommodation_amount = fields.Monetary('Accommodation', digits=(16, 2), required=True, help="Employee's monthly gross Basic Salary.")
    transportation_amount = fields.Monetary('Transportation Allowance', digits=(16, 2), required=True, help="Employee's monthly gross Basic Salary.")