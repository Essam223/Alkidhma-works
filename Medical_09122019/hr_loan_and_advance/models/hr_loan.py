# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError
from odoo.tools import email_split, float_is_zero
import time
from odoo.exceptions import UserError, AccessError, ValidationError


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread']
    _description = "Loan Request"

    @api.one
    def _compute_loan_emi(self):
        self.emi_count = self.env['hr.loan.line'].search_count([('loan_id', '=', self.id)])

    emi_count = fields.Integer(string="EMI Count", compute='_compute_loan_emi')

    @api.one
    def _compute_loan_amount(self):
        total_paid = 0.0
        for loan in self:
            for line in loan.loan_lines:
                if line.state == 'Paid':
                    total_paid += line.amount
            # Modifications needed........
            balance_amount = loan.loan_amount - total_paid
            self.total_amount = loan.loan_amount
            self.balance_amount = balance_amount
            self.total_paid_amount = total_paid

    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')

    def _default_journal_id(self):
        company =  self.env['res.company']._company_default_get('res.partner')
        if self.company_id:
            company =  self.company_id
        journals = self.env['account.journal'].search([('company_id', '=', company.id), ('name', 'ilike', 'HR loan'),
                                            ('type', 'in', ('bank', 'cash'))], limit=1)
        return journals

    def _default_currency(self):
        return self.env['res.company']._company_default_get('res.partner').currency_id

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.currency_id = self.company_id.currency_id
        if self.account_id and self.account_id.company_id != self.company_id:
            self.account_id = False
        if self.journal_id.company_id != self.company_id:
            journal_id = self._default_journal_id()
            self.journal_id = journal_id
            self.account_id = journal_id.default_credit_account_id.id
        self.employee_id = False
        account_id_domain = self._get_account_id()
        journal_id_domain = self._get_journal_id()
        return {
            'domain': {'account_id': account_id_domain, 'journal_id':journal_id_domain}
        }

    def _get_journal_id(self):
        domain = [('company_id', '=', self.company_id.id), ('name', 'ilike', 'HR loan'), ('type', 'in', ('bank', 'cash'))]
        return domain

    def _get_account_id(self):
        bank_cash =  self.env.ref('account.data_account_type_liquidity').id
        domain = [('company_id', '=', self.company_id.id), ('name', 'ilike', 'HR loan'),
                  ('user_type_id', '=', bank_cash)]
        return domain

    name = fields.Char(string="Loan Name", default="/", readonly=True)
    date = fields.Date(string="Issue Date", default=fields.Date.today(), readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=True,
                                  states={'draft': [('readonly', False)]}, domain="[('company_id', '=', company_id)]")
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,
                                    string="Department")
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position")
    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 default=_default_company,
                                 states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=_default_currency, domain="[('company_id', '=', company_id)]")
    payment_start_date = fields.Date(string="Payment Start Date", required=True, default=fields.Date.today(),
                                     readonly=True, states={'draft': [('readonly', False)]})
    payment_end_date = fields.Date(string="Payment End Date", required=True, readonly=True, states={'draft': [('readonly', False)]})
    installment = fields.Integer(string="No of Installments", default=1, readonly=True, states={'draft': [('readonly', False)]})
    loan_amount = fields.Float(string="Loan Amount", required=True, readonly=True,
                               states={'draft': [('readonly', False)]})
    emi = fields.Float(string="EMI", readonly=True, states={'draft': [('readonly', False)]})
    total_amount = fields.Float(string="Total Amount", readonly=True, compute='_compute_loan_amount')
    total_paid_amount = fields.Float(string="Amount Paid", compute='_compute_loan_amount')
    balance_amount = fields.Float(string="Balance Amount", compute='_compute_loan_amount')
    loan_lines = fields.One2many('hr.loan.line', 'loan_id', string="Installments", index=True, readonly=True, states={'draft': [('readonly', False)]})

    @api.onchange('loan_amount', 'installment')
    def onchange_loan_amount(self):
        if self.installment and self.loan_amount:
            self.emi = self.loan_amount / self.installment

    @api.onchange('loan_amount', 'emi')
    def onchange_loan_amount_emi(self):
        if self.emi and self.loan_amount:
            self.installment = self.loan_amount / self.emi

    @api.constrains('emi')
    def _check_wage_emi(self):
        for loan in self:
            if loan.employee_id.contract_id:
                if loan.employee_id.contract_id.wage < loan.emi:
                    raise ValidationError(_('EMI should be less than Basic salary'))

    @api.onchange('payment_start_date', 'installment')
    def onchange_payment_start_date(self):
        if self.payment_start_date and self.installment >=1:
            self.payment_end_date = datetime.strptime(self.payment_start_date, '%Y-%m-%d') +\
                                    relativedelta(months=self.installment-1)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('approve', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False)
    color_tree = fields.Char(compute='_compute_color', string='Color Index')

    def _compute_color(self):
        today = datetime.strptime(time.strftime("%Y-%m-%d"), '%Y-%m-%d').date()
        for loan in self:
            if loan.state != 'disbursed':
                loan.color_tree = 1
            if loan.state == 'disbursed':
                payment_end_date = datetime.strptime(loan.payment_end_date, '%Y-%m-%d').date()
                payment_start_date = datetime.strptime(loan.payment_start_date, '%Y-%m-%d').date()
                if payment_start_date <= today <= payment_end_date:
                    loan.color_tree = 3
                else:
                    loan.color_tree = 2
                all_emi_paid = all(emi_lines.state == 'Paid' for emi_lines in loan.loan_lines)
                if all_emi_paid:
                    loan.color_tree = 2

    journal_id = fields.Many2one('account.journal', string='Loan Journal',
                                 default=_default_journal_id,
                                 help="The journal used when the loan is done.",
                                 readonly=True, states={'draft': [('readonly', False)],
                                                        'waiting_approval_1': [('readonly', False)],
                                                        'approve': [('readonly', False)]},
                                 domain=_get_journal_id)

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            self.account_id = self.journal_id.default_credit_account_id.id

    account_id = fields.Many2one('account.account', string='Account', help="An loan account is expected",
                                 readonly=True, domain=_get_account_id,
                                 states={'draft': [('readonly', False)],
                                                        'waiting_approval_1': [('readonly', False)],
                                                        'approve': [('readonly', False)]})
    account_move_id = fields.Many2one('account.move', string='Journal Entry', ondelete='restrict', copy=False, readonly=True)

    @api.constrains('payment_start_date', 'payment_end_date', 'employee_id')
    def _check_date_employee_id(self):
        for loan in self:
            domain_same_time = [
                ('payment_start_date', '<=', loan.payment_end_date),
                ('payment_end_date', '>=', loan.payment_start_date),
                ('employee_id', '=', loan.employee_id.id),
                ('id', '!=', loan.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            nloans = self.search_count(domain_same_time)
            if nloans:
                raise ValidationError(_('You cannot have 2 loans that overlaps on same day for %s !')
                                      % (loan.employee_id.name))

    @api.constrains('balance_amount', 'employee_id')
    def _check_balance_amount_employee_id(self):
        for loan in self:
            domain_pending_ins = [
                ('employee_id', '=', loan.employee_id.id),
                ('id', '!=', loan.id),
                ('balance_amount', '!=', 0),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            nloans_pend = self.search_count(domain_pending_ins)
            if nloans_pend:
                raise ValidationError(_('%s has a pending installment') % (loan.employee_id.name))

    @api.constrains('company_id', 'doctor', 'journal_id', 'employee_id')
    def _check_same_company_appt(self):
        if self.company_id:
            if self.account_id.company_id:
                if self.company_id.id != self.account_id.company_id.id:
                    raise ValidationError(_('Error ! Account and Appointment should be of same company'))
            if self.journal_id.company_id:
                if self.company_id.id != self.journal_id.company_id.id:
                    raise ValidationError(_('Error ! Journal and Appointment should be of same company'))
            if self.employee_id.company_id:
                if self.company_id.id != self.employee_id.company_id.id:
                    raise ValidationError(_('Error ! Employee and Appointment should be of same company'))

    @api.model
    def create(self, values):
        # loan_count = self.env['hr.loan'].search_count([('employee_id', '=', values['employee_id']),
        #                                                # ('state', '=', 'disbursed'),
        #                                                # ('state', '=', 'approve'),
        #                                                ('state', 'not in', ('refuse', 'cancel')),
        #                                                ('balance_amount', '!=', 0)])
        # if loan_count:
        #     raise except_orm('Error!', 'The employee has a pending installment')
        # else:
            values['name'] = self.env['ir.sequence'].get('hr.loan.seq') or ' '
            res = super(HrLoan, self).create(values)
            return res

    @api.multi
    def action_refuse(self):
        return self.write({'state': 'refuse'})

    @api.multi
    def action_submit(self):
        self.compute_installment()
        self.write({'state': 'waiting_approval_1'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    def get_current_login_user_mail(self):
        if self.env.user.partner_id.email:
            return self.env.user.partner_id.email
        return self.company_id.email

    @api.multi
    def action_approve(self):
        template_id = self.env.ref('hr_loan_and_advance.email_template_edi_loan')
        template_id.with_context(lang=self.env.user.lang).send_mail(self.id, force_send=True, raise_exception=False)
        self.write({'state': 'approve'})
        return True

    @api.multi
    def _compute_loan_totals(self, company_currency, account_move_lines, move_date):
        self.ensure_one()
        total = 0.0
        total_currency = 0.0
        for line in account_move_lines:
            line['currency_id'] = False
            line['amount_currency'] = False
            if self.currency_id != company_currency:
                line['currency_id'] = self.currency_id.id
                line['amount_currency'] = line['price']
                line['price'] = self.currency_id.with_context(
                    date=move_date or fields.Date.context_today(self)).compute(line['price'], company_currency)
            total -= line['price']
            total_currency -= line['amount_currency'] or line['price']
        return total, total_currency, account_move_lines

    def _prepare_move_line(self, line):
        partner_id = self.employee_id.address_home_id.commercial_partner_id.id
        return {
            'date_maturity': line.get('date_maturity'),
            'partner_id': partner_id,
            'name': line['name'][:64],
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and - line['price'],
            'account_id': line['account_id'],
            'analytic_line_ids': line.get('analytic_line_ids'),
            'amount_currency': line['price'] > 0 and abs(line.get('amount_currency')) or - abs(line.get('amount_currency')),
            'currency_id': line.get('currency_id'),
            'tax_line_id': line.get('tax_line_id'),
            'tax_ids': line.get('tax_ids'),
            'quantity': line.get('quantity', 1.00),
            'product_id': line.get('product_id'),
            'product_uom_id': line.get('uom_id'),
            'analytic_account_id': line.get('analytic_account_id'),
            'payment_id': line.get('payment_id'),
            'expense_id': line.get('expense_id'),
        }

    @api.multi
    def disburse_loan(self):
        for loan in self:
            if loan.state != 'approve':
                raise UserError(_("You can only generate accounting entry for approved loan request."))
            if not loan.journal_id:
                raise UserError(_("Loan request must have a journal specified to generate accounting entries."))
            journal = loan.journal_id
            acc_date = loan.date
            move = self.env['account.move'].create({
                'journal_id': journal.id,
                'company_id': loan.company_id.id,
                'date': acc_date,
                'ref': loan.name,
                'name': '/',
                'narration': 'HR Loan Disburse',
            })
            account_move = []
            account = ""
            if loan.account_id:
                account = loan.account_id
            if not account:
                raise UserError(_('Please configure Default loan account'))
            move_line = {
                'type': 'src',
                'name': loan.employee_id.name + ': ' + loan.name,
                'price': -loan.loan_amount,
                'account_id': account.id,
            }
            account_move.append(move_line)
            company_currency = loan.company_id.currency_id
            diff_currency_p = loan.currency_id != company_currency
            total, total_currency, move_lines = loan._compute_loan_totals(company_currency, account_move, acc_date)
            if not loan.employee_id.address_home_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    loan.employee_id.name))
            if loan.employee_id.address_home_id:
                emp_account = loan.employee_id.address_home_id.property_account_payable_id.id
                aml_name = loan.employee_id.name + ': ' + loan.name
                move_lines.append({
                    'type': 'dest',
                    'name': aml_name,
                    'price': total,
                    'account_id': emp_account,
                    'date_maturity': acc_date,
                    'amount_currency': diff_currency_p and total_currency or False,
                    'currency_id': diff_currency_p and loan.currency_id.id or False,
                })
                lines = [(0, 0, loan._prepare_move_line(x)) for x in move_lines]
                move.with_context(dont_create_taxes=True).write({'line_ids': lines})
                loan.write({'account_move_id': move.id})
                move.post()
            loan.write({'state': 'disbursed'})
        return True

    @api.multi
    def compute_installment(self):
        for loan in self:
            date_start = datetime.strptime(loan.payment_start_date, '%Y-%m-%d')
            amount = loan.loan_amount / loan.installment
            for i in range(1, loan.installment + 1):
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
        return True


class InstallmentLine(models.Model):
    _name = "hr.loan.line"
    _inherit = ['mail.thread']
    _description = "Installment Line"

    date = fields.Date(string="Payment Date", required=True, track_visibility='onchange')
    amount = fields.Float(string="Amount", required=True, track_visibility='onchange')
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.", track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string="Employee", related='loan_id.employee_id', track_visibility='onchange')
    paid_manually = fields.Boolean(string="Paid Manually", track_visibility='onchange')
    loan_state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('approve', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="Loan State", related='loan_id.state', track_visibility='onchange', copy=False)
    state = fields.Selection([
        ('payment_pending', 'Payment pending'),
        ('waiting_for_postponed', 'Waiting for postponement'),
        ('Postponed', 'Postponed'),
        ('Paid', 'Paid'),
    ], string="State", default='payment_pending', track_visibility='onchange', copy=False)
    account_move_id = fields.Many2one('account.move', string='Journal Entry', ondelete='restrict', copy=False,
                                      readonly=True)
    emi_postponed_date = fields.Date(string="EMI Postpone Date", track_visibility='onchange')
    emi_postponed_reason = fields.Text(string="EMI Postpone Reason", track_visibility='onchange')

    def accept_postpone_request(self):
        self.write({'state': 'Postponed', 'date':self.emi_postponed_date})

    def reject_postpone_request(self):
        self.write({'state': 'payment_pending', 'emi_postponed_date': False, 'emi_postponed_reason': False})


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.one
    def _compute_employee_loans(self):
        self.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', self.id)])

    loan_count = fields.Integer(string="Loan Count", compute='_compute_employee_loans')

    def get_loan_ins(self, employee, date_from, date_to):
        employee_id = self.env['hr.employee'].browse(employee)
        dom = [('employee_id', '=', employee_id.id), ('loan_state', '=', 'disbursed'), ('state', '!=', 'Paid'),
               ('date', '>=', date_from), ('date', '<=', date_to)]
        loan_line_amount = 0.0
        for loan_line in self.env['hr.loan.line'].search(dom):
            loan_line.write({'state': 'Paid'})
            loan_line_amount += loan_line.amount
        return loan_line_amount


