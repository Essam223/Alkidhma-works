# -*- coding: utf-8 -*-
import datetime, time
from dateutil import relativedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def get_all_allowances(self, employee, payslip):
        payslip_id = self.env['hr.payslip'].browse(payslip)
        contract_id = payslip_id.contract_id
        if contract_id:
            total_allowance = 0.0
            for each_allow in contract_id.allowance_contract_ids:
                total_allowance += each_allow.allowance_amount
            return total_allowance
        return 0