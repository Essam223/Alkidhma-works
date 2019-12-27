# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, exceptions
from odoo.exceptions import UserError
from lxml import etree as E
from xml.dom import minidom
from random import *
from lxml import etree
import base64, datetime


class CheckoutOnly(models.TransientModel):
    _name = 'checkout.only'
    _description = 'Checkout'

    @api.model
    def default_get(self, fields):
        record_ids = self._context.get('active_ids')
        result = super(CheckoutOnly, self).default_get(fields)
        if record_ids:
            if 'employee_ids' in fields:
                employee_ids = self.env['hr.employee'].browse(record_ids).ids
                result['employee_ids'] = employee_ids
        return result

    employee_ids = fields.Many2many('hr.employee', 'merge_employee_rel_out', 'checkout_id', 'employee_id',
                                    string='Employee')
    check_out_time = fields.Datetime('Checkout Time', default=fields.Datetime.now, required=True)

    @api.multi
    def action_checkout_only(self):
        self.ensure_one()
        for employee in self.employee_ids:
            last_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('department_id', '=', employee.department_id.id),
                ('check_out', '=', False),
            ], order='check_in desc', limit=1)
            if not last_check_in:
                raise exceptions.ValidationError(_(
                    "No active Check in record for %(empl_name)s, In order to Check out, Please Check in.") % {
                                                     'empl_name': employee.name})
            last_check_in[0].write({'check_out': self.check_out_time})
