# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date, datetime


class Employee(models.Model):
    _inherit = "hr.employee"

    # def _get_remaining_leaves(self):
    #     """ Helper to compute the remaining leaves for the current employees
    #         :returns dict where the key is the employee id, and the value is the remain leaves
    #     """
    #     self._cr.execute("""
    #         SELECT
    #             sum(h.number_of_days) AS days,
    #             h.employee_id
    #         FROM
    #             hr_holidays h
    #             join hr_holidays_status s ON (s.id=h.holiday_status_id)
    #         WHERE
    #             h.state='validate' AND
    #             s.limit=False AND
    #             h.employee_id in %s AND
    #             h.date_carry_forward >= %s
    #         GROUP BY h.employee_id""", (tuple(self.ids), date.today()))
    #     return dict((row['employee_id'], row['days']) for row in self._cr.dictfetchall())

    # @api.multi
    # def _compute_leaves_count(self):
    #     leaves = self.env['hr.holidays'].read_group([
    #         ('employee_id', 'in', self.ids),
    #         ('holiday_status_id.limit', '=', False),
    #         ('state', '=', 'validate'),
    #         ('date_carry_forward', '>=', date.today())
    #     ], fields=['number_of_days', 'employee_id'], groupby=['employee_id'])
    #     mapping = dict([(leave['employee_id'][0], leave['number_of_days']) for leave in leaves])
    #     for employee in self:
    #         employee.leaves_count = mapping.get(employee.id)


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    unpaid_leave = fields.Boolean('Unpaid Leave')

    @api.multi
    def get_days(self, employee_id):
        # need to use `dict` constructor to create a dict per id
        result = dict(
            (id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0, virtual_remaining_leaves=0)) for id in self.ids)

        holidays = self.env['hr.holidays'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['confirm', 'validate1', 'validate']),
            ('holiday_status_id', 'in', self.ids)
        ])

        for holiday in holidays:
            status_dict = result[holiday.holiday_status_id.id]
            if holiday.type == 'add':
                if holiday.state == 'validate':
                    # note: add only validated allocation even for the virtual
                    # count; otherwise pending then refused allocation allow
                    # the employee to create more leaves than possible
                    if not holiday.is_carry_forward_leave and holiday.date_carry_forward and datetime.strptime(holiday.date_carry_forward,
                                                                                    '%Y-%m-%d').date() >= date.today():
                        status_dict['virtual_remaining_leaves'] += holiday.number_of_days_temp
                        status_dict['max_leaves'] += holiday.number_of_days_temp
                        status_dict['remaining_leaves'] += holiday.number_of_days_temp
            elif holiday.type == 'remove':  # number of days is negative
                status_dict['virtual_remaining_leaves'] -= holiday.number_of_days_temp
                if holiday.state == 'validate':
                    status_dict['leaves_taken'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] -= holiday.number_of_days_temp
        return result


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_Unpaid_deductions(self, employee, payslip, date_from, date_to):
        total_hour = 0
        worked_hour = 0
        unpaid_hour = 0
        one_hr_slry = 0
        if payslip:
            payslip_id = self.env['hr.payslip'].browse(payslip)
            for rec in payslip_id.worked_days_line_ids:
                if rec.code != 'OVTH' and rec.code != 'OVTW':
                    total_hour += rec.number_of_hours
                # if rec.name == 'Normal Working Days paid at 100%':
                #     worked_hour += rec.number_of_hours
                if rec.name == 'UNPAID' or rec.name=='Unpaid':
                    unpaid_hour += rec.number_of_hours
            # total_hour = worked_hour + unpaid_hour
            if total_hour:
                one_hr_slry = payslip_id.contract_id.wage / round(total_hour, 2)
        return round(unpaid_hour * one_hr_slry, 2)
