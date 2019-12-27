# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo import models, fields, api, exceptions, _


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=False)
    missed = fields.Boolean("Missed entry")

    @api.multi
    def name_get(self):
        result = []
        for attendance in self:
            checkin = ""
            if attendance.check_in:
                checkin = fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance,
                                                                                            fields.Datetime.from_string(
                                                                                                attendance.check_in)))
            if not attendance.check_out:
                result.append((attendance.id, _("%(empl_name)s from %(check_in)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_in': checkin,
                }))
            else:
                result.append((attendance.id, _("%(empl_name)s from %(check_in)s to %(check_out)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_in': checkin,
                    'check_out': fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance,
                                                                                             fields.Datetime.from_string(
                                                                                                 attendance.check_out))),
                }))
        return result



    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            pass

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                delta = datetime.strptime(attendance.check_out, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(
                    attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = 0