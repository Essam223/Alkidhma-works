# -*- coding: utf-8 -*-
import datetime, time
from dateutil import relativedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    payment_ids = fields.Many2many('account.payment', 'payslip_payment_rel', 'payslip_id', 'payment_id',
                                   string="Payments", copy=False, readonly=True)
    residual = fields.Float('Due Amount', compute='_compute_residual', copy=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('confirmed', 'Confirmed'),
        ('done', 'Paid'),
        ('cancel', 'Rejected'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft',
        help="""* When the payslip is created the status is \'Draft\'
                    \n* If the payslip is under verification, the status is \'Waiting\'.
                    \n* If the payslip is confirmed then status is set to \'Confirmed\'.
                    \n* If the payslip is paid, then status is set to \'Done\'.
                    \n* When user cancel payslip the status is \'Rejected\'.""")

    @api.depends('payment_ids')
    def _compute_residual(self):
        for rec in self:
            net_salary = rec.net_salary
            paid_amt = 0
            for line in rec.payment_ids:
                paid_amt += line.amount
            due = net_salary - paid_amt
            rec.residual = due


    @api.multi
    def action_payslip_done(self):
        if not self.line_ids and not self.number:
            self.compute_sheet()
        precision = self.env['decimal.precision'].precision_get('Payroll')
        net_amount = 0.0
        for slip in self:
            line_ids = []
            date = slip.date or slip.date_to
            name = _('Payslip of %s') % (slip.employee_id.name)
            move_dict = {
                'narration': name,
                'ref': slip.number,
                'journal_id': slip.journal_id.id,
                'date': date,
            }
            net_amount = 0.0
            for lines in slip.details_by_salary_rule_category:
                if lines.category_id.id == self.env.ref('hr_payroll.NET').id:
                    net_amount = lines.total
            partner_id = slip.employee_id.address_home_id
            if float_is_zero(net_amount, precision_digits=precision):
                continue
            if not slip.journal_id.default_debit_account_id:
                raise UserError(_('Please define Debit account for journal: %s')% (slip.journal_id.name))
            if not partner_id:
                raise UserError(_('Please define Private Address for Employee: %s')% (slip.employee_id.name))
            credit_account_id = False
            if partner_id.property_account_payable_id:
                credit_account_id = partner_id.property_account_payable_id.id
            if partner_id.commercial_partner_id.id:
                credit_account_id = partner_id.commercial_partner_id.property_account_payable_id.id
            if not credit_account_id:
                raise UserError(_('Please define Payable Account for this Employee.'))
            debit_account_id = slip.journal_id.default_debit_account_id.id
            if net_amount:
                debit_line = (0, 0, {
                    'name':  slip.name,
                    'partner_id': partner_id.id,
                    'account_id': debit_account_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': net_amount > 0.0 and net_amount or 0.0,
                    'credit': net_amount < 0.0 and -net_amount or 0.0,
                })
                line_ids.append(debit_line)
                credit_line = (0, 0, {
                    'name':  slip.name,
                    'partner_id': partner_id.id,
                    'account_id': credit_account_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': net_amount < 0.0 and -net_amount or 0.0,
                    'credit': net_amount > 0.0 and net_amount or 0.0,
                })
                line_ids.append(credit_line)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            slip.write({'move_id': move.id, 'date': date})
            move.post()
        return self.write({'state': 'confirmed', 'residual': net_amount})