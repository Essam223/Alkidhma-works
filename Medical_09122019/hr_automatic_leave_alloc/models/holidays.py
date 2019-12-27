# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, AccessError, ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    joining_date = fields.Date('Joining Date')


class HrHoliday(models.Model):
    _inherit = 'hr.holidays'

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for holiday in self:
            if holiday.type == 'remove':
                domain = [
                    ('date_from', '<=', holiday.date_to),
                    ('date_to', '>=', holiday.date_from),
                    ('employee_id', '=', holiday.employee_id.id),
                    ('id', '!=', holiday.id),
                    ('type', '=', 'remove'),
                    ('state', 'not in', ['cancel', 'refuse']),
                ]
                nholidays = self.search_count(domain)
                if nholidays:
                    raise ValidationError(_('You can not have 2 leaves that overlaps on same day!'))

    @api.model
    def run_monthly_scheduler(self):
        leave_status_obj = self.env['hr.holidays.status']
        leave_status_ids = leave_status_obj.search([('auto_allocation', '=', True)])
        employee_obj = self.env['hr.employee']
        employee_ids = employee_obj.search([('active', '=', True)])
        # employee_ids = employee_obj.search([('active', '=', True), ('contract_ids', '!=', False)])
        for leave_status in leave_status_ids:
            for employee in employee_ids:
                if leave_status.allocation_range == 'year':
                    if employee.joining_date:
                        joining_date = datetime.strptime(employee.joining_date, '%Y-%m-%d')
                    else:
                        continue
                    test_date = joining_date.date()
                    delta = relativedelta(years=1)
                    while test_date <= date.today():
                        # if leave_status.id == self.env.ref('hr_holidays.holiday_status_cl').id:
                            one_year_added = relativedelta(years=1)
                            x_year_completed = test_date + one_year_added
                            allocate_ids = self.search([('allocation_date', '=', x_year_completed.strftime("%Y-%m-%d")),
                                                        ('number_of_days_temp', '=', leave_status.days_to_allocate),
                                                        ('type', '=', 'add'),
                                                        ('employee_id', '=', employee.id),
                                                        ('holiday_status_id', '=', leave_status.id)],
                                                       )
                            date_carry_forward_yearly = False
                            if not leave_status.is_carry_forward_leave:
                                date_carry_forward_yearly = x_year_completed + one_year_added
                            if not allocate_ids and date.today() >= x_year_completed:
                                vals = {
                                    'name': 'Yearly Allocation of ' + leave_status.name,
                                    'number_of_days_temp': leave_status.days_to_allocate,
                                    'type': 'add',
                                    'employee_id': employee.id,
                                    'holiday_status_id': leave_status.id,
                                    'allocation_date':  x_year_completed,
                                    'allocation_range':  leave_status.allocation_range,
                                    'date_carry_forward': date_carry_forward_yearly,
                                    'is_carry_forward_leave': leave_status.is_carry_forward_leave,
                                }
                                leave_id = self.create(vals)
                            test_date += delta
                        # else:
                        #     allocate_ids = self.search([('allocation_date', '=', test_date.strftime("%Y-%m-%d")),
                        #                                 ('number_of_days_temp', '=', leave_status.days_to_allocate),
                        #                                 ('type', '=', 'add'),
                        #                                 ('employee_id', '=', employee.id),
                        #                                 ('holiday_status_id', '=', leave_status.id)],
                        #                                )
                        #     one_year_added = relativedelta(years=1)
                        #     date_carry_forward_yearly = False
                        #     if not leave_status.is_carry_forward_leave:
                        #         date_carry_forward_yearly = test_date + one_year_added
                        #     if not allocate_ids:
                        #         vals = {
                        #             'name': 'Yearly Allocation of ' + leave_status.name,
                        #             'number_of_days_temp': leave_status.days_to_allocate,
                        #             'type': 'add',
                        #             'employee_id': employee.id,
                        #             'holiday_status_id': leave_status.id,
                        #             'allocation_date': test_date,
                        #             'allocation_range': leave_status.allocation_range,
                        #             'date_carry_forward': date_carry_forward_yearly,
                        #             'is_carry_forward_leave': leave_status.is_carry_forward_leave,
                        #         }
                        #         leave_id = self.create(vals)
                        #     test_date += delta
                if leave_status.allocation_range == 'month':
                    if employee.joining_date:
                        joining_date = datetime.strptime(employee.joining_date, '%Y-%m-%d')
                    else:
                        continue
                    test_date = joining_date.date()
                    delta = relativedelta(months=1)
                    while test_date <= date.today():
                        # Cant use this hr_holidays.holiday_status_cl for multicompany
                        # if leave_status.id == self.env.ref('hr_holidays.holiday_status_cl').id:
                            one_month_added = relativedelta(months=1)
                            x_month_completed = test_date + one_month_added
                            allocate_ids = self.search([('allocation_date', '=', x_month_completed.strftime("%Y-%m-%d")),
                                                        ('number_of_days_temp', '=', leave_status.days_to_allocate),
                                                        ('type', '=', 'add'),
                                                        ('employee_id', '=', employee.id),
                                                        ('holiday_status_id', '=', leave_status.id)],
                                                       )
                            date_carry_forward_monthly = False
                            if not leave_status.is_carry_forward_leave:
                                date_carry_forward_monthly = x_month_completed + one_month_added
                            if not allocate_ids and date.today() >= x_month_completed:
                                vals = {
                                    'name': 'Monthly Allocation of ' + leave_status.name,
                                    'number_of_days_temp': leave_status.days_to_allocate,
                                    'type': 'add',
                                    'employee_id': employee.id,
                                    'holiday_status_id': leave_status.id,
                                    'allocation_date':  x_month_completed,
                                    'allocation_range':  leave_status.allocation_range,
                                    'date_carry_forward': date_carry_forward_monthly,
                                    'is_carry_forward_leave': leave_status.is_carry_forward_leave,
                                }
                                leave_id = self.create(vals)
                            test_date += delta
                        # else:
                        #     allocate_ids = self.search([('allocation_date', '=', test_date.strftime("%Y-%m-%d")),
                        #                                 ('number_of_days_temp', '=', leave_status.days_to_allocate),
                        #                                 ('type', '=', 'add'),
                        #                                 ('employee_id', '=', employee.id),
                        #                                 ('holiday_status_id', '=', leave_status.id)],
                        #                                )
                        #     if not allocate_ids:
                        #         one_month_added = relativedelta(months=1)
                        #         date_carry_forward_monthly = False
                        #         if not leave_status.is_carry_forward_leave:
                        #             date_carry_forward_monthly = test_date + one_month_added
                        #         vals = {
                        #             'name': 'Monthly Allocation of ' + leave_status.name,
                        #             'number_of_days_temp': leave_status.days_to_allocate,
                        #             'type': 'add',
                        #             'employee_id': employee.id,
                        #             'holiday_status_id': leave_status.id,
                        #             'allocation_date':  test_date,
                        #             'allocation_range': leave_status.allocation_range,
                        #             'date_carry_forward':  date_carry_forward_monthly ,
                        #             'is_carry_forward_leave': leave_status.is_carry_forward_leave,
                        #         }
                        #         leave_id = self.create(vals)
                        #     test_date += delta