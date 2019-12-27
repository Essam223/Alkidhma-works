# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo import exceptions, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    contract_id = fields.Many2one('hr.contract', compute='_compute_contract_id', string='Current Contract',
                                  help='Latest contract of the employee')
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', compute='_compute_contract_id')
    date_start = fields.Date('Start Date', compute='_compute_contract_id',
                             help="Start date of the contract.")
    wage = fields.Float('Wage', digits=(16, 2), required=True, help="Employee's monthly gross wage.",
                           compute='_compute_contract_id')

    def _compute_contract_id(self):
        """ get the lastest contract """
        Contract = self.env['hr.contract']
        for employee in self:
            contract_id = Contract.search([('employee_id', '=', employee.id), ('state', '!=', 'close')],
                                          order='date_start desc', limit=1)
            employee.contract_id = contract_id
            if contract_id:
                employee.struct_id = contract_id.struct_id.id
                employee.wage = contract_id.wage
                employee.date_start = contract_id.date_start
            else:
                employee.struct_id = False
                employee.wage = 0.0
                employee.date_start = ""
