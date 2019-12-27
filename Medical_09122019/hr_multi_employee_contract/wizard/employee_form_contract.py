# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import Warning


class EmployeeContractWiz(models.TransientModel):
    _name = 'employee.form.contract'

    name = fields.Char("Name", required=True)
    wage = fields.Integer('Wage', required=True)
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', required=True)
    working_hours = fields.Many2one('resource.calendar', 'Working Hours')
    company_id = fields.Many2one('res.company', 'Company')

    @api.model
    def default_get(self, fields):
        res = super(EmployeeContractWiz, self).default_get(fields)
        employees = self.env['hr.employee'].browse(self._context.get('active_ids', False))
        # emp_list = []
        # for employee in employees:
        #     emp_list.append((0, 0, {'employee_id': employee.id}))
        res['company_id'] = employees.company_id.id
        res['name'] = 'Employment contract - ' + str(employees.name)
        res['struct_id'] = employees.job_id.struct_id.id
        res['working_hours'] = employees.resource_calendar_id.id
        return res

    @api.multi
    def create_employee_contract(self):
        employee_id = self.env['hr.employee'].browse(self._context.get('active_ids', False))

        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id),
                                                      ('state', 'not in', ['close', 'cancel'])], order="date_start desc")
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
             'struct_id': self.struct_id.id,
             'resource_calendar_id': self.working_hours.id})
        if employee_id.joining_date:
            contract_vals['date_start'] = employee_id.joining_date
        action = self.env.ref('hr_contract.action_hr_contract').read()[0]
        action['views'] = [(self.env.ref('hr_contract.hr_contract_view_form').id, 'form')]
        action['res_id'] = contract_vals.id
        return action