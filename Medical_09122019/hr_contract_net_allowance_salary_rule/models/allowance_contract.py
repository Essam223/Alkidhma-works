# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import Warning


class HrAllowance(models.Model):
    _name = 'hr.allowance'

    name = fields.Char("Name", required=True)


class AllowanceWizContract(models.TransientModel):
    _name = 'allowance.wiz.contract'

    allowance_id = fields.Many2one('hr.allowance', string='Allowance', required=True)
    allowance_amount = fields.Integer('Amount', required=True)
    employee_form_contract_id = fields.Many2one('employee.form.contract', string='Single Contract Creation Wizard')
    multi_contract_id = fields.Many2one('multi.contract', string='Multi Contract Creation Wizard')


class AllowanceContract(models.Model):
    _name = 'allowance.contract'

    allowance_id = fields.Many2one('hr.allowance', string='Allowance', required=True)
    allowance_amount = fields.Integer('Amount', required=True)
    contract_id = fields.Many2one('hr.contract', string='Contract')