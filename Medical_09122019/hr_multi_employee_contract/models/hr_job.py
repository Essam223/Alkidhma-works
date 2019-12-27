# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo import exceptions, fields


class HrJob(models.Model):
    _inherit = 'hr.job'

    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
