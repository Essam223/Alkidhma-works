# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
import datetime
from odoo.osv import expression
from datetime import timedelta, date


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    include_in_offer_letter = fields.Boolean(string='Include in Offer Letter')
