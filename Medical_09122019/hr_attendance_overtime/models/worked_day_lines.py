# -*- coding: utf-8 -*-
import logging
from datetime import timedelta, datetime
from odoo import models, fields, api, _, exceptions
from datetime import time as datetime_time, date
import time, pytz
_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def compute_sheet(self):
        for payslip in self:
            contract_ids = payslip.contract_id.ids or payslip.get_contract(payslip.employee_id, payslip.date_from,
                                                                        payslip.date_to)
            contract_ids_list = self.env['hr.contract'].browse(contract_ids)
            payslip.worked_days_line_ids = False
            payslip.input_line_ids = False
            worked_days_line_ids = payslip.get_worked_day_lines(contract_ids_list, payslip.date_from, payslip.date_to)
            input_line_ids = payslip.get_inputs(contract_ids_list, payslip.date_from, payslip.date_to)
            payslip.worked_days_line_ids = worked_days_line_ids
            payslip.input_line_ids = input_line_ids
            payslip.onchange_employee_id(payslip.date_from, payslip.date_to, payslip.employee_id.id, payslip.contract_id)
        return super(HrPayslip, self).compute_sheet()

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        # additional start....................
        all_total_hours_worked = 0
        all_working_day_hours = 0
        all_working_day_hours_ot = 0
        all_holiday_hours_ot = 0
        work_data_hours = 0
        all_holiday_dates = []
        global_holiday_dates = []
        working_holiday_dates = []
        all_week_list = [0, 1, 2, 3, 4, 5, 6]
        working_week_list = []
        check_in_list = []
        count_w_h = 0
        count_holi = 0
        total_hours = 0
        number_of_days = 0
        uom_day = self.env.ref('product.product_uom_day', raise_if_not_found=False)
        contract_id = []
        contract_val = False
        # additional end......................
        res = []
        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
            day_from = datetime.combine(fields.Date.from_string(date_from), datetime_time.min)
            day_to = datetime.combine(fields.Date.from_string(date_to), datetime_time.max)
            # compute leave days
            leaves = {}
            # additional start....................
            contract_val = contracts
            # additional end......................
            day_leave_intervals = contract.employee_id.iter_leaves(day_from, day_to, calendar=contract.resource_calendar_id)
            for day_intervals in day_leave_intervals:
                # print day_intervals
                for interval in day_intervals:
                    holiday = interval[2]['leaves'].holiday_id
                    # additional start....................
                    name_code = 'Leave'
                    if holiday.holiday_status_id:
                        name_code = holiday.holiday_status_id.name
                        if holiday.holiday_status_id.unpaid_leave:
                            name_code = 'UNPAID'
                    if not holiday.holiday_status_id:
                        if interval[2]['leaves']:
                            name_code = interval[2]['leaves'].name
                    if not name_code:
                        name_code = 'LEAVE'
                    current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                        'name': name_code,
                        'sequence': 5,
                        'code': name_code,
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'contract_id': contract.id,
                    })
                    # additional end....................
                    leave_time = (interval[1] - interval[0]).seconds / 3600
                    current_leave_struct['number_of_hours'] += leave_time
                    work_hours = contract.employee_id.get_day_work_hours_count(interval[0].date(), calendar=contract.resource_calendar_id)
                    current_leave_struct['number_of_days'] += leave_time / work_hours
                    # Unpaid leave code.......................
                    if not holiday.holiday_status_id.unpaid_leave:
                        work_data_hours += leave_time
            # compute worked days
            work_data = contract.employee_id.get_work_days_data(day_from, day_to, calendar=contract.resource_calendar_id)
            # print work_data, work_data_hours
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': work_data['days'],
                'number_of_hours': work_data['hours'],
                'contract_id': contract.id,
            }
            res.append(attendances)
            res.extend(leaves.values())
            # additional start....................
            work_data_hours += work_data['hours']
            # additional end....................
        # additional start....................
        date_from = fields.Datetime.from_string(date_from)
        date_from += timedelta(days=-1)
        date_from = str(date_from)
        date_to = fields.Datetime.from_string(date_to)
        date_to += timedelta(days=1)
        date_to = str(date_to)
        days_list = []
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        if contract_val:
            resource_calendar_id = contract_val.resource_calendar_id
            attn_lines_first = self.env['hr.attendance'].search([('check_in', '>=', date_from), ('check_out', '<=', date_to),
                                                                ('employee_id', '=', contract_val.employee_id.id)])

            for attn_lines in attn_lines_first:
                display_date_checkin = datetime.strftime(pytz.utc.localize(datetime.strptime(attn_lines.check_in, '%Y-%m-%d %H:%M:%S')).astimezone(local),"%Y-%m-%d %H:%M:%S")
                c_in = fields.Datetime.from_string(display_date_checkin) - timedelta(hours=.5)
                _logger.info('attn_lines.check_in ..........................: %s', attn_lines.check_in)
                if c_in.date() not in check_in_list:
                    check_in_list.append(c_in.date())
                working_days = resource_calendar_id.attendance_ids
                for w_working_day in working_days:
                    if w_working_day.dayofweek not in working_week_list:
                        working_week_list.append(w_working_day.dayofweek)
                check_in_first = datetime.strptime(attn_lines.check_in, '%Y-%m-%d %H:%M:%S')
                check_out_first = datetime.strptime(attn_lines.check_out, '%Y-%m-%d %H:%M:%S')
                time_diff = check_out_first - check_in_first
                total_hours += ((time_diff.seconds / 60) / 60)
                check_in_date = datetime.strptime(attn_lines.check_in, '%Y-%m-%d %H:%M:%S')
                if check_in_date.date() not in days_list:
                    days_list.append(check_in_date.date())
                global_holiday = resource_calendar_id.global_leave_ids
                for g_l in global_holiday:
                    if not g_l.holiday_id:
                        global_date_from = datetime.strftime(pytz.utc.localize(datetime.strptime(g_l.date_from, '%Y-%m-%d %H:%M:%S')).astimezone(local), "%Y-%m-%d %H:%M:%S")
                        global_date_to = datetime.strftime( pytz.utc.localize(datetime.strptime(g_l.date_to, '%Y-%m-%d %H:%M:%S')).astimezone(local), "%Y-%m-%d %H:%M:%S")
                        g_l_date_from = fields.Datetime.from_string(global_date_from) - timedelta(hours=.5)
                        g_l_date_to = fields.Datetime.from_string(global_date_to) - timedelta(hours=.5)
                        if g_l_date_from.date() not in global_holiday_dates:
                            global_holiday_dates.append(g_l_date_from.date())
                        if g_l_date_to.date() not in global_holiday_dates:
                            global_holiday_dates.append(g_l_date_to.date())
            for holiday_week in working_week_list:
                for attn_lines_2 in attn_lines_first:
                    display_date_checkin_2 = datetime.strftime(pytz.utc.localize(datetime.strptime(attn_lines_2.check_in, '%Y-%m-%d %H:%M:%S')).astimezone(local),"%Y-%m-%d %H:%M:%S")
                    c_in_2 = fields.Datetime.from_string(display_date_checkin_2) - timedelta(hours=.5)
                    if int(c_in_2.date().weekday()) == int(holiday_week):
                        if c_in_2.date() not in working_holiday_dates:
                            working_holiday_dates.append(c_in_2.date())
            all_holiday_dates = global_holiday_dates
            for each_holi in list(set(check_in_list).difference(set(working_holiday_dates))):
                if each_holi not in all_holiday_dates:
                    all_holiday_dates.append(each_holi)
            for attn_lines_3 in attn_lines_first:
                display_date_checkin_3 = datetime.strftime(pytz.utc.localize(datetime.strptime(attn_lines_3.check_in, '%Y-%m-%d %H:%M:%S')).astimezone(local),"%Y-%m-%d %H:%M:%S")
                display_date_checkout_3 = datetime.strftime(pytz.utc.localize(datetime.strptime(attn_lines_3.check_out, '%Y-%m-%d %H:%M:%S')).astimezone(local),"%Y-%m-%d %H:%M:%S")
                c_in_3 = fields.Datetime.from_string(display_date_checkin_3) - timedelta(hours=.5)
                c_out_3 = fields.Datetime.from_string(display_date_checkout_3) - timedelta(hours=.5)
                if c_in_3.date() in all_holiday_dates:
                    count_holi +=1
                    diff_3 = c_out_3 - c_in_3
                    days_tot_3, seconds_tot_3 = diff_3.days, diff_3.seconds
                    all_holiday_hours_ot += days_tot_3 * 24 + seconds_tot_3 // 3600
            for attn_lines in attn_lines_first:
                display_date_checkin = datetime.strftime(pytz.utc.localize(datetime.strptime(attn_lines.check_in, '%Y-%m-%d %H:%M:%S')).astimezone(local),"%Y-%m-%d %H:%M:%S")
                display_date_checkout = datetime.strftime(pytz.utc.localize(datetime.strptime(attn_lines.check_out, '%Y-%m-%d %H:%M:%S')).astimezone(local),"%Y-%m-%d %H:%M:%S")
                c_in = fields.Datetime.from_string(display_date_checkin) - timedelta(hours=.5)
                c_out = fields.Datetime.from_string(display_date_checkout) - timedelta(hours=.5)
                if c_in.date() not in check_in_list:
                    check_in_list.append(c_in.date())
                work_hours_here = resource_calendar_id.get_work_hours_count(c_in, c_out, resource_calendar_id.id)
                all_working_day_hours += work_hours_here
                diff = c_out - c_in
                # print attn_lines,attn_lines.check_in,display_date_checkin, c_in
                days_tot, seconds_tot = diff.days, diff.seconds
                total_hours_here = days_tot * 24 + seconds_tot // 3600
                all_total_hours_worked += total_hours_here
                for holiday_week in working_week_list:
                    _logger.info('OVTW c_in ..........................: %s  %s  %s', c_in, work_hours_here, total_hours_here)
                    if int(c_in.weekday()) == int(holiday_week):
                        # print c_in.weekday(),"***********", holiday_week, work_hours_here, total_hours_here
                        if int(work_hours_here) < int(total_hours_here):
                        # if int(work_hours_here) != int(total_hours_here):
                        #     print count_w_h, "=========="
                            count_w_h += 1
            if work_data_hours:
                all_working_day_hours_ot = all_total_hours_worked - work_data_hours - all_holiday_hours_ot
            # print all_total_hours_worked , work_data_hours,all_holiday_hours_ot
            if all_holiday_hours_ot:
                res.append({
                    'code': 'OVTH',
                    'contract_id': contract_val.id,
                    'number_of_days': count_holi,
                    'number_of_hours': all_holiday_hours_ot ,
                    'name': 'Holidays Overtime Hours',
                })
            _logger.info('OVTW TEST ..........................: %s', count_w_h)
            if all_working_day_hours_ot > 0:
                res.append({
                    'code': 'OVTW',
                    'contract_id': contract_val.id,
                    'number_of_days': count_w_h,
                    'number_of_hours': all_working_day_hours_ot ,
                    'name': 'Working days Overtime Hours',
                })
        # additional end....................
        return res


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def get_overtime_ins_holiday(self, employee, payslip):
        overtime_holiday_timesheet = 0
        if payslip:
            payslip_id = self.env['hr.payslip'].browse(payslip)
            total_hour = 0
            over_time_holiday_hrs = 0
            for rec in payslip_id.worked_days_line_ids:
                if rec.name == 'Holidays Overtime Hours' or rec.code == 'OVTH':
                    over_time_holiday_hrs += rec.number_of_hours
                # if rec.name == 'Normal Working Days paid at 100%':
                if rec.code != 'OVTW' and rec.code != 'OVTH':
                    total_hour += rec.number_of_hours
            if total_hour:
                old_one_hr_slry = payslip_id.contract_id.wage / total_hour
                overtime_hourly_rate_holiday = self.env['ir.config_parameter'].sudo().get_param('hr_attendance_overtime.overtime_hourly_rate_holiday')
                overtime_holiday_timesheet = ((old_one_hr_slry * float(overtime_hourly_rate_holiday)) * over_time_holiday_hrs)
        return overtime_holiday_timesheet

    def get_overtime_ins_working_day(self, employee, payslip):
        overtime_working_day_timesheet = 0
        if payslip:
            payslip_id = self.env['hr.payslip'].browse(payslip)
            total_hour = 0
            over_time_working_day_hrs = 0
            for rec in payslip_id.worked_days_line_ids:
                if rec.name == 'Working days Overtime Hours' or rec.code == 'OVTW':
                    over_time_working_day_hrs += rec.number_of_hours
                # if rec.name == 'Normal Working Days paid at 100%':
                if rec.code != 'OVTW' and rec.code != 'OVTH':
                    total_hour += rec.number_of_hours
            if total_hour:
                old_one_hr_slry = payslip_id.contract_id.wage / total_hour
                overtime_hourly_rate_working_day = self.env['ir.config_parameter'].sudo().get_param('hr_attendance_overtime.overtime_hourly_rate_working_day')
                overtime_working_day_timesheet = ((old_one_hr_slry * float(overtime_hourly_rate_working_day)) * over_time_working_day_hrs)
        return overtime_working_day_timesheet
