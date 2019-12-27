# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError
from odoo.tools import email_split, float_is_zero
import time
from odoo.exceptions import UserError, AccessError, ValidationError


class PayLoanIndividual(models.TransientModel):
    _name = 'pay.loan.individual'
    _description = 'Pay Loan Individual'

    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')

    @api.onchange('company_id')
    def onchange_company_id(self):
        journal_id_domain = self._get_journal_id()
        return {
            'domain': {'journal_id': journal_id_domain}
        }

    def _get_journal_id(self):
        domain = [('company_id', '=', self.company_id.id), ('name', 'not ilike', 'HR loan'), ('type', 'in', ('bank', 'cash'))]
        return domain

    loan_line_id = fields.Many2one('hr.loan.line', 'Loan line')
    company_id = fields.Many2one('res.company', 'Company', readonly=True, default=_default_company)
    journal_id = fields.Many2one('account.journal', 'Payment Journal',required=True, domain=_get_journal_id)

    @api.model
    def default_get(self, fields):
        res = super(PayLoanIndividual, self).default_get(fields)
        loan_line = self.env['hr.loan.line'].browse(self.env.context.get('active_ids'))
        res['loan_line_id'] = loan_line.id
        res['company_id'] = loan_line.loan_id.company_id.id
        return res

    @api.multi
    def action_pay(self):
        loan_line = self.loan_line_id
        for loan in loan_line:
            journal = self.journal_id
            acc_date = loan.date
            move = self.env['account.move'].create({
                'journal_id': journal.id,
                'company_id': loan.loan_id.company_id.id,
                'date': acc_date,
                'ref': loan.loan_id.name + ' ' + acc_date + ' Payment',
                'name': '/',
                'narration': 'HR Loan Manual Payment for Date'+ ' ' + acc_date,
            })
            account_move = []
            account = ""
            if loan.loan_id.account_id:
                account = loan.loan_id.account_id
            if not account:
                raise UserError(_('Please configure Default loan account'))
            move_line = {
                'type': 'dest',
                'name': loan.loan_id.employee_id.name + ': ' + loan.loan_id.name + ' ' + acc_date + ' Payment',
                'price': loan.amount,
                'account_id': account.id,
            }
            account_move.append(move_line)
            company_currency = loan.loan_id.company_id.currency_id
            diff_currency_p = loan.loan_id.currency_id != company_currency
            total, total_currency, move_lines = loan.loan_id._compute_loan_totals(company_currency, account_move, acc_date)
            if not loan.loan_id.employee_id.address_home_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    loan.loan_id.employee_id.name))
            if loan.loan_id.employee_id.address_home_id:
                emp_account = loan.loan_id.employee_id.address_home_id.property_account_payable_id.id
                aml_name = loan.loan_id.employee_id.name + ': ' + loan.loan_id.name+ ' ' + acc_date + ' Payment'
                move_lines.append({
                    'type': 'src',
                    'name': aml_name,
                    'price': total,
                    'account_id': emp_account,
                    'date_maturity': acc_date,
                    'amount_currency': diff_currency_p and total_currency or False,
                    'currency_id': diff_currency_p and loan.loan_id.currency_id.id or False,
                })
                lines = [(0, 0, loan.loan_id._prepare_move_line(x)) for x in move_lines]
                move.with_context(dont_create_taxes=True).write({'line_ids': lines})
                loan.write({'account_move_id': move.id})
                move.post()
        loan_line.write({'state': 'Paid', 'paid_manually':True})

