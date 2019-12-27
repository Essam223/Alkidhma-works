# -*- coding: utf-8 -*-
import datetime, time
from dateutil import relativedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class EmployeeContractWiz(models.TransientModel):
    _inherit = 'employee.form.contract'

    wage = fields.Integer('Basic Salary', required=True)
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', required=True)
    journal_id = fields.Many2one('account.journal', 'Salary Journal', required=True, domain="[('company_id', '=', company_id)]")
    date_start = fields.Date('Joining Date', required=True, default=fields.Date.today,
                             help="Joining date of the contract.")
    allowance_wiz_contract_ids = fields.One2many('allowance.wiz.contract', 'employee_form_contract_id', string='Allowances')

    @api.model
    def default_get(self, fields):
        res = super(EmployeeContractWiz, self).default_get(fields)
        res['struct_id'] = self.env.ref('hr_payroll.structure_base').id
        return res

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
            'journal_id': self.journal_id.id,
            'date_start': self.date_start,
            'struct_id': self.struct_id.id,
            'resource_calendar_id': self.working_hours.id})
        contract_vals.write({'resource_calendar_id':self.working_hours.id})
        for allowance_ids in self.allowance_wiz_contract_ids:
            allow_contract_vals = {
                'allowance_id': allowance_ids.allowance_id.id,
                'allowance_amount': allowance_ids.allowance_amount,
                'contract_id': contract_vals.id,
            }
            self.env['allowance.contract'].create(allow_contract_vals)
        employee_id.write({'resource_calendar_id':self.working_hours.id, 'joining_date': self.date_start})
        action = self.env.ref('hr_contract.action_hr_contract').read()[0]
        action['views'] = [(self.env.ref('hr_contract.hr_contract_view_form').id, 'form')]
        action['res_id'] = contract_vals.id
        return action