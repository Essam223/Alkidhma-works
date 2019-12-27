# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import base64, datetime
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
HOURS_PER_DAY = 8
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class ExtendLeave(models.TransientModel):
    _name = 'extend.leave'
    _description = 'Extend Leave'

    @api.model
    def default_get(self, fields):
        result = super(ExtendLeave, self).default_get(fields)
        holiday_rec = self.env['hr.holidays'].browse(self._context['active_ids'])
        if holiday_rec:
            # if no extended leaves, of if with cancel or refused state
            date_to_here = holiday_rec.date_to
            if not holiday_rec.extended_ids:
                new_format = datetime.datetime.strptime(holiday_rec.date_to,
                                           DEFAULT_SERVER_DATETIME_FORMAT)
                result['extend_from'] = new_format + timedelta(seconds=1)
            if holiday_rec.extended_ids:
                if any(ext_leaves.state in ['draft', 'confirm', 'validate1'] for ext_leaves in holiday_rec.extended_ids):
                    raise ValidationError(_('One Extension request is under processing'))
                if any(ext_leaves.state == 'validate' for ext_leaves in holiday_rec.extended_ids):
                    date_to_list = [ext_leaves.date_to for ext_leaves in holiday_rec.extended_ids]
                    if len(date_to_list) == 1:
                        date_to_here = date_to_list[0]
                    else:
                        larger_date_to = date_to_list[0]
                        for each_date_to in date_to_list:
                            if each_date_to > larger_date_to:
                                larger_date_to = each_date_to
                        date_to_here = larger_date_to
            new_format = datetime.datetime.strptime(date_to_here,
                                                        DEFAULT_SERVER_DATETIME_FORMAT)
            result['extend_from'] = new_format + timedelta(seconds=1)
            return result

    extend_from = fields.Datetime(string="Extend from", required=True)
    extend_to = fields.Datetime(string="Extend to", required=True)
    extend_dur = fields.Float(
        'Duration', help='Number of days of the leave request according to your working schedule.')

    @api.onchange('extend_to')
    def _onchange_extend_to(self):
        """ Update the number_of_days. """
        extend_from = self.extend_from
        extend_to = self.extend_to
        holiday_rec = self.env['hr.holidays'].browse(self._context['active_ids'])

        # Compute and update the number of days
        if (extend_to and extend_from) and (extend_from < extend_to):
            self.extend_dur = holiday_rec._get_number_of_days(extend_from, extend_to, holiday_rec.employee_id.id)
        else:
            self.extend_dur = 0
        if (extend_to and extend_from) and (extend_from >= extend_to):
            raise ValidationError(_('From Date Should be less than the To Date!'))

    leave_type = fields.Many2one('hr.holidays.status', string="Remaining leaves by type", required=True)

    def create_new_leave_vals(self, leave_type, holiday_rec, date_from, date_to):
        Holidays = self.env['hr.holidays']
        vals = {
                'name': 'Extension (Type: ' + leave_type.name + ' )',
                'holiday_status_id': leave_type.id,
                'date_from': date_from,
                'date_to': date_to,
                'employee_id': holiday_rec.employee_id.id,
                'department_id': holiday_rec.employee_id.department_id.id,
                'type': 'remove',
                'state': 'confirm',
                'holiday_type': holiday_rec.holiday_type,
                'holidays_ext_id': holiday_rec.id,
            }
        LeaveCreated = Holidays.create(vals)
        # LeaveCreated._onchange_employee()
        LeaveCreated._onchange_date_from()
        LeaveCreated._onchange_date_to()

    @api.multi
    def action_extend_leave(self):
        self.ensure_one()
        if not self._context.get('active_ids'):
            return {'type': 'ir.actions.act_window_close'}
        Holidays = self.env['hr.holidays']
        holiday_rec = self.env['hr.holidays'].browse(self._context['active_ids'])
        if (self.extend_to and self.extend_from) and (self.extend_from >= self.extend_to):
            raise ValidationError(_('From Date Should be less than the To Date!'))

        existing_leave_type = holiday_rec.holiday_status_id
        existing_leave_days = existing_leave_type.get_days(holiday_rec.employee_id.id)[existing_leave_type.id]
        # a) If can Override Limit OR duration <= remaining leave exists on existing leave type , allocate with existing leave type
        # b) If duration > remaining leave exists on existing leave type, allocate with new new leave type m2one field in wizard
        # b1) Both leave types are equal and not sufficient
        # b2) If can Override Limit OR duration <= remaining leave exists on new leave type , allocate with new leave type
        # b3) If duration > remaining leave exists on new leave type, raise Warning
        if existing_leave_type.limit or self.extend_dur <= existing_leave_days['remaining_leaves']:
            self.create_new_leave_vals(existing_leave_type, holiday_rec, self.extend_from, self.extend_to)
        else:
            new_leave_type = self.leave_type
            new_leave_days = new_leave_type.get_days(holiday_rec.employee_id.id)[new_leave_type.id]
            if existing_leave_days['remaining_leaves']:
                intermed_date = datetime.datetime.strptime(self.extend_from, '%Y-%m-%d %H:%M:%S')
                delta = relativedelta(minutes=60)
                # ----------------------------check if needed.............start
                if existing_leave_days['remaining_leaves'] > 1:
                    intermed_date += relativedelta(days=existing_leave_days['remaining_leaves']-1)
                # ----------------------------check if needed.............end
                while holiday_rec._get_number_of_days(self.extend_from, str(intermed_date),
                                                      holiday_rec.employee_id.id) < existing_leave_days['remaining_leaves']:
                    intermed_date += delta
                if new_leave_type.limit or self.extend_dur <= new_leave_days['remaining_leaves']:
                    self.create_new_leave_vals(existing_leave_type, holiday_rec, self.extend_from, intermed_date)
                    self.create_new_leave_vals(new_leave_type, holiday_rec, intermed_date+relativedelta(seconds=1), self.extend_to)
                else:
                    raise ValidationError(_('Leave is not sufficient for %s') % new_leave_type.name)
            else:
                if new_leave_type.limit or self.extend_dur <= new_leave_days['remaining_leaves']:
                    self.create_new_leave_vals(new_leave_type, holiday_rec, self.extend_from, self.extend_to)
                else:
                    raise ValidationError(_('Leave is not sufficient for %s') % new_leave_type.name)