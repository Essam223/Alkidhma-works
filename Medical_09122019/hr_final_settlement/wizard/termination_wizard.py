from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta


class TerminationWizard(models.TransientModel):
    _name = 'termination.wizard'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    joining_date = fields.Date('Joining Date')
    last_working_day = fields.Date('Last working day', required=True)

    @api.multi
    def action_confirm(self):
        wizard_vals = self.read()[0]
        if wizard_vals['employee_id']:
            joining_date = datetime.strptime(self.joining_date, '%Y-%m-%d')
            last_working_day = datetime.strptime(self.last_working_day, '%Y-%m-%d')
            worked_days_delta = relativedelta(last_working_day, joining_date)
            one_day_salary = self.employee_id.wage / 30
            gratuity_days = 0
            if worked_days_delta.years <= 4 and worked_days_delta.years >= 1:
                gratuity_days = worked_days_delta.years * 21
            if worked_days_delta.years >= 5:
                gratuity_days = worked_days_delta.years * 28
            gratuity_amt = gratuity_days * one_day_salary
            employee_id = self.env['hr.employee'].browse(wizard_vals['employee_id'][0])
            vals = {
                'employee_id': employee_id.id,
                'joining_date': self.joining_date,
                'last_working_day': self.last_working_day,
                'gratuity_days': gratuity_days,
                'gratuity_amt': gratuity_amt,
            }
            self.env['termination.details'].create(vals)
