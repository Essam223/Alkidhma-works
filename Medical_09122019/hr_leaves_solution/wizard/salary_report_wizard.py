from odoo import api, fields, models, SUPERUSER_ID
import base64
from odoo.exceptions import Warning


class SalaryReportWizard(models.TransientModel):
    _name = "salary.report.wizard"

    period_start = fields.Date("Period From", required=True, default=fields.Date.context_today)
    period_stop = fields.Date("Period To", required=True, default=fields.Date.context_today)
    employee_id = fields.Many2one('hr.employee', "Employee")
    show_description = fields.Boolean(string='Display Description', default=True)

    @api.multi
    def salary_report(self):
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'employee_id': self.employee_id.name,
            'show_description': self.show_description,
                }
        return self.env.ref('hr_leaves_solution.salary_report').report_action(self, data=data)


class ReportSalary(models.AbstractModel):

    _name = 'report.hr_leaves_solution.salary_report_pdf'

    @api.model
    def get_salary_details(self, period_start=False, period_stop=False, employee_id=False, show_description=False):
        dom = [
            ('date_from', '>=', period_start),
            ('date_from', '<=', period_stop),
            ('state', 'in', ('confirmed', 'done'))
        ]
        if employee_id:
            dom.append(('employee_id', '=', employee_id))
        payslips = self.env['hr.payslip'].search(dom)

        payslip_list = []
        for order in payslips:
            order_data = {
                'number': order.number,
                'employee_id': order.employee_id.name,
                'date_from': order.date_from,
                'date_to': order.date_to,
                'net_salary': order.net_salary,
                'residual': order.residual,
                'company_id': order.company_id,
                'payslip': order,
                'paid_amount': order.net_salary - order.residual,
            }
            payslip_list.append(order_data)
        return {
            'orders': sorted(payslip_list, key=lambda l: l['number']),
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_salary_details(data['period_start'],
                                          data['period_stop'],
                                          data['employee_id'], data['show_description']))
        return data
