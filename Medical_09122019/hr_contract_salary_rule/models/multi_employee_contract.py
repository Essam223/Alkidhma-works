# -*- coding: utf-8 -*-
import datetime, time
from dateutil import relativedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class MultiEmployeeWiz(models.TransientModel):
    _inherit = 'multi.employee'

    # @api.model
    # def _get_default_struct(self):
    #     return self.env.ref('hr_payroll.structure_base', False)

    wage = fields.Integer('Basic Salary', required=True)
    accommodation_amount = fields.Integer('Accommodation', required=True)
    transportation_amount = fields.Integer('Transportation Allowance', required=True)
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', required=True)
    journal_id = fields.Many2one('account.journal', 'Salary Journal', required=True)
    date_start = fields.Date('Joining Date', required=True, default=fields.Date.today,
                             help="Joining date of the contract.")

class MultiContractWiz(models.TransientModel):
    _inherit = 'multi.contract'



    @api.model
    def default_get(self, fields):
        res = super(MultiContractWiz, self).default_get(fields)
        for emp in res['employee_ids']:
            emp[2]['struct_id'] = self.env.ref('hr_payroll.structure_base').id
        return res

    @api.multi
    def multi_employee_contract(self):
        multi_employees = self.env['multi.employee'].search([('active', '=', True)])
        contract_id = self.env['hr.contract'].search([('employee_id', 'in', [
            emp.employee_id.id for emp in self.employee_ids]),
                                                      ('state', 'not in', ['close', 'cancel'])],
                                                     order="date_start desc")
        if contract_id:
            raise Warning(_('Contract already exist of employee %s.') % ",".join(
                [contract.employee_id.name for contract in contract_id]))
        for emp_id in self.employee_ids:
            contract_vals = self.env['hr.contract'].create({
                'name': emp_id.name,
                'state': 'open',
                'employee_id': emp_id.employee_id.id,
                'job_id': emp_id.employee_id.job_id.id,
                'department_id': emp_id.employee_id.department_id.id,
                'wage': emp_id.wage,
                'accommodation_amount': emp_id.accommodation_amount,
                'transportation_amount': emp_id.transportation_amount,
                'journal_id': emp_id.journal_id.id,
                'date_start': emp_id.date_start,
                'struct_id': emp_id.struct_id.id,
                'working_hours': emp_id.working_hours.id})
            action = self.env.ref('hr_contract.action_hr_contract').read()[0]
            action['views'] = [(self.env.ref('hr_contract.hr_contract_view_form').id, 'form')]
            action['res_id'] = contract_vals.id
        multi_employees.unlink()
        return action

    @api.multi
    def create_employee_contract(self):
        employee_id = self.env['hr.employee'].browse(self._context.get('active_ids', False))

        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id),
                                                      ('state', 'not in', ['close', 'cancel'])],
                                                     order="date_start desc")
        if contract_id:
            raise Warning(_('Contract already exist of employee %s.') % ",".join(
                [contract.employee_id.name for contract in contract_id]))
        contract_vals = self.env['hr.contract'].create({
            'name': self.name,
            'state': 'open',
            'employee_id': employee_id.id,
            'job_id': employee_id.job_id.id,
            'department_id': employee_id.department_id.id,
            'wage': self.wage,
            'accommodation_amount': self.accommodation_amount,
            'transportation_amount': self.transportation_amount,
            'journal_id': self.journal_id.id,
            'date_start': self.date_start,
            'struct_id': self.struct_id.id,
            'working_hours': self.working_hours.id})
        # contract_vals.write({'working_hours':self.working_hours.id})
        # employee_id.write({'working_hours':self.working_hours.id})
        action = self.env.ref('hr_contract.action_hr_contract').read()[0]
        action['views'] = [(self.env.ref('hr_contract.hr_contract_view_form').id, 'form')]
        action['res_id'] = contract_vals.id
        return action