# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, fields, models, _


class MultiEmployeeWiz(models.TransientModel):
    _inherit = 'multi.employee'

    wage = fields.Integer('Basic Salary', required=True)
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', required=True)
    journal_id = fields.Many2one('account.journal', 'Salary Journal', required=True, domain="[('company_id', '=', company_id)]")
    date_start = fields.Date('Joining Date', required=True, default=fields.Date.today,
                             help="Joining date of the contract.")


class MultiContractWiz(models.TransientModel):
    _inherit = 'multi.contract'

    allowance_multi_wiz_contract_ids = fields.One2many('allowance.wiz.contract', 'multi_contract_id',
                                                       string='Allowances')

    @api.model
    def default_get(self, fields):
        res = super(MultiContractWiz, self).default_get(fields)
        for emp in res['employee_ids']:
            # emp[2]['date_start'] = date.today().strftime('%m/%d/%Y')
            emp[2]['struct_id'] = self.env.ref('hr_payroll.structure_base').id
        return res

    @api.multi
    def multi_employee_contract(self):
        multi_employees = self.env['multi.employee'].search([('active', '=', True)])
        contract_id = self.env['hr.contract'].search([('state', 'not in', ['close', 'cancel']),
                      ('employee_id', 'in', [emp.employee_id.id for emp in self.employee_ids])],
                      order="date_start desc")
        if contract_id:
            raise Warning(_('Contract already exist for employee %s.')
                          % ",".join([contract.employee_id.name for contract in contract_id]))
        for emp_id in self.employee_ids:
            emp_id.employee_id.write({'resource_calendar_id': emp_id.working_hours.id, 'joining_date': emp_id.date_start})
            contract_vals = self.env['hr.contract'].create({
                'name': emp_id.name,
                'state': 'open',
                'employee_id': emp_id.employee_id.id,
                'job_id': emp_id.employee_id.job_id.id,
                'department_id': emp_id.employee_id.department_id.id,
                'wage': emp_id.wage,
                'journal_id': emp_id.journal_id.id,
                'date_start': emp_id.date_start,
                'struct_id': emp_id.struct_id.id,
                'resource_calendar_id': emp_id.working_hours.id})
            for allowance_ids in self.allowance_multi_wiz_contract_ids:
                allow_contract_vals = {
                    'allowance_id': allowance_ids.allowance_id.id,
                    'allowance_amount': allowance_ids.allowance_amount,
                    'contract_id': contract_vals.id,
                }
                self.env['allowance.contract'].create(allow_contract_vals)
        multi_employees.unlink()