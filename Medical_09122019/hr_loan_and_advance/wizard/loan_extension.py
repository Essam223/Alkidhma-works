# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError
from odoo.tools import email_split, float_is_zero
import time
from odoo.exceptions import UserError, AccessError, ValidationError


class LoanExtension(models.TransientModel):
    _name = 'loan.extension.wiz'
    _description = 'Loan Extension'

    emi_postponed_date = fields.Date(string="EMI Postpone Date", track_visibility='onchange', required=True)
    emi_postponed_reason = fields.Text(string="EMI Postpone Reason", track_visibility='onchange', required=True)
    loan_line_id = fields.Many2one('hr.loan.line', 'Loan line')

    @api.model
    def default_get(self, fields):
        res = super(LoanExtension, self).default_get(fields)
        loan_line = self.env['hr.loan.line'].browse(self.env.context.get('active_ids'))
        res['loan_line_id'] = loan_line.id
        return res

    @api.multi
    def button_extend_loan(self):
        self.loan_line_id.write({'emi_postponed_date': self.emi_postponed_date,
                                 'emi_postponed_reason':self.emi_postponed_reason,
                                 'state': 'waiting_for_postponed'})

