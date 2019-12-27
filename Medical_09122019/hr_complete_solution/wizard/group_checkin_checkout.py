# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, exceptions
from odoo.exceptions import UserError
from lxml import etree as E
from xml.dom import minidom
from random import *
from lxml import etree
import base64, datetime


class CheckinCheckout(models.TransientModel):
    _name = 'checkin.checkout'
    _description = 'Checkin/Checkout'

    @api.model
    def default_get(self, fields):
        record_ids = self._context.get('active_ids')
        result = super(CheckinCheckout, self).default_get(fields)
        if record_ids:
            if 'employee_ids' in fields:
                employee_ids = self.env['hr.employee'].browse(record_ids).ids
                result['employee_ids'] = employee_ids
        return result

    employee_ids = fields.Many2many('hr.employee', 'merge_employee_rel', 'checkin_checkout_id', 'employee_id',
                                    string='Employee')
    check_in_time = fields.Datetime('Checkin Time', default=fields.Datetime.now, required=True)
    check_out_time = fields.Datetime('Checkout Time', default=fields.Datetime.now, required=True)

    @api.multi
    def action_checkin_checkout(self):
        self.ensure_one()
        for employee in self.employee_ids:
            last_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('department_id', '=', employee.department_id.id),
                ('check_out', '=', False),
            ], order='check_in desc', limit=1)
            if last_check_in:
                raise exceptions.ValidationError(_(
                    "Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out") % {
                                                     'empl_name': employee.name})
            self.env['hr.attendance'].create({
                'employee_id': employee.id,
                'department_id': employee.department_id.id,
                'check_in': self.check_in_time,
                'check_out': self.check_out_time,
            })
