# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from lxml import etree
from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


SEQ_TYPE = {
    'sale': 'voucher.receipt',
    'purchase': 'voucher.payment',
}


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'
    _description = 'Accounting Voucher'
    # _inherit = ['mail.thread']
    _order = "date desc, id desc"

    def set_amt_in_worlds(self):
        # amount_in_words += '\tOnly'
        self.amt_in_words = self.currency_id.amount_to_text(self.amount)

    amt_in_words = fields.Char(compute='set_amt_in_worlds')
    voucher_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase')
    ], string='Type', readonly=True, states={'draft': [('readonly', False)]}, oldname="type")
    name = fields.Char('Payment Reference',
                       readonly=True, states={'draft': [('readonly', False)]}, default='')
    date = fields.Datetime("Bill Date", readonly=True, required=True,
                       index=True, states={'draft': [('readonly', False)]},
                       copy=False, default=fields.Date.context_today)
    account_date = fields.Date("Accounting Date",
                               readonly=True, index=True, states={'draft': [('readonly', False)]},
                               help="Effective date for accounting entries", copy=False,
                               default=fields.Date.context_today)
    journal_id = fields.Many2one('account.journal', 'Journal', domain=[('type', 'in', ('bank', 'cash'))],
                                 required=True, readonly=True, states={'draft': [('readonly', False)]})
    account_id = fields.Many2one('account.account', 'Account',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]}
                                 , domain=[('deprecated', '=', False)])
                                 # domain="[('deprecated', '=', False), ('internal_type','=', 'liquidity')]")
    line_ids = fields.One2many('account.voucher.line', 'voucher_id', 'Voucher Lines',
                               readonly=True, copy=True,
                               states={'draft': [('readonly', False)]})
    narration = fields.Text('Notes', readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', compute='_get_journal_currency',
                                  string='Currency', readonly=True, required=True,
                                  default=lambda self: self._get_currency())
    company_id = fields.Many2one('res.company', 'Company',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 related='journal_id.company_id', default=lambda self: self._get_company())
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('proforma', 'Pro-forma'),
        ('posted', 'Posted')
    ], 'Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Voucher.\n"
             " * The 'Pro-forma' status is used when the voucher does not have a voucher number.\n"
             " * The 'Posted' status is used when user create voucher,a voucher number is generated and voucher entries are created in account.\n"
             " * The 'Cancelled' status is used when user cancel voucher.")
    reference = fields.Char('Bill Reference', readonly=True, states={'draft': [('readonly', False)]},
                            help="The partner reference of this document.", copy=False)
    amount = fields.Monetary(string='Total', store=True, compute='_compute_total', required=True, readonly=True,
                             default=0.0)
    tax_amount = fields.Monetary(readonly=True, store=True, compute='_compute_total')
    tax_correction = fields.Monetary(readonly=True, states={'draft': [('readonly', False)]},
                                     help='In case we have a rounding problem in the tax, use this field to correct it')
    number = fields.Char(readonly=True, copy=False)
    partner_name = fields.Char('Name', readonly=True, states={'draft': [('readonly', False)]})
    move_id = fields.Many2one('account.move', 'Journal Entry', copy=False)
    partner_id = fields.Many2one('res.partner', 'Partner', change_default=1, readonly=True,
                                 states={'draft': [('readonly', False)]})
    partner_account_id = fields.Many2one('account.account')
    payed_to_name = fields.Char(string="Paid To")
    paid = fields.Boolean(compute='_check_paid', help="The Voucher has been totally paid.")
    pay_now = fields.Selection([
        ('pay_now', 'Pay Directly'),
        ('pay_later', 'Pay Later'),
    ], 'Payment', index=True, readonly=True, states={'draft': [('readonly', False)]}, default='pay_now')
    date_due = fields.Date('Due Date', readonly=True, index=True, states={'draft': [('readonly', False)]})

    @api.onchange('partner_id')
    def partner_change(self):
        for i in self:
            if i.partner_id:
                i.partner_name = i.partner_id.name

    @api.depends('amount')
    def set_amt_in_words(self):
        # amount_in_words += '\tOnly'
        self.amt_in_words = self.currency_id.amount_to_text(self.amount)

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id and self.journal_id.type in ('bank', 'cash'):
            self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
            self.account_id = self.voucher_type == 'purchase' and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id
        return {}

    @api.one
    @api.depends('move_id.line_ids.reconciled', 'move_id.line_ids.account_id.internal_type')
    def _check_paid(self):
        self.paid = any([((line.account_id.internal_type, 'in', ('receivable', 'payable')) and line.reconciled) for line in self.move_id.line_ids])

    @api.model
    def _get_currency(self):
        journal = self.env['account.journal'].browse(self._context.get('journal_id', False))
        if journal.currency_id:
            return journal.currency_id.id
        return self.env.user.company_id.currency_id.id

    @api.model
    def _get_company(self):
        return self._context.get('company_id', self.env.user.company_id.id)

    @api.multi
    @api.depends('name', 'number')
    def name_get(self):
        return [(r.id, (r.number or _('Voucher'))) for r in self]

    @api.one
    @api.depends('journal_id', 'company_id')
    def _get_journal_currency(self):
        self.currency_id = self.journal_id.currency_id.id or self.company_id.currency_id.id

    @api.multi
    @api.depends('tax_correction', 'line_ids.price_subtotal')
    def _compute_total(self):
        for voucher in self:
            if voucher.line_ids:
                total = 0
                tax_amount = 0
                for line in voucher.line_ids:
                    tax_info = line.tax_ids.compute_all(line.price_unit, voucher.currency_id, line.quantity,
                                                        line.product_id, voucher.partner_id)
                    total += tax_info.get('total_included', 0.0)
                    tax_amount += sum([t.get('amount', 0.0) for t in tax_info.get('taxes', False)])
                voucher.amount = total + voucher.tax_correction
                voucher.tax_amount = tax_amount

    # @api.one
    # @api.depends('account_pay_now_id', 'account_pay_later_id', 'pay_now')
    # def _get_account(self):
    #     self.account_id = self.account_pay_now_id if self.pay_now == 'pay_now' else self.account_pay_later_id

    @api.onchange('date')
    def onchange_date(self):
        self.account_date = self.date

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.partner_account_id = self.partner_id.property_account_receivable_id \
            if self.voucher_type == 'sale' else self.partner_id.property_account_payable_id

    @api.multi
    def proforma_voucher(self):
        self.action_move_line_create()

    @api.multi
    def action_cancel_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def cancel_voucher(self):
        for voucher in self:
            voucher.move_id.button_cancel()
            voucher.move_id.unlink()
        self.write({'state': 'cancel', 'move_id': False})

    @api.multi
    def unlink(self):
        for voucher in self:
            if voucher.state not in ('draft', 'cancel'):
                raise UserError(_('Cannot delete voucher(s) which are already opened or paid.'))
            res = super(AccountVoucher, voucher).unlink()
        return res

    @api.multi
    def first_move_line_get(self, move_id, company_currency, current_currency):
        debit = credit = 0.0
        if self.voucher_type == 'purchase':
            credit = self._convert_amount(self.amount)
        elif self.voucher_type == 'sale':
            debit = self._convert_amount(self.amount)
        if debit < 0.0: debit = 0.0
        if credit < 0.0: credit = 0.0
        sign = debit - credit < 0 and -1 or 1
        # set the first line of the voucher
        move_line = {
            'name': self.name or '/',
            'debit': debit,
            'credit': credit,
            'account_id': self.account_id.id,
            'move_id': move_id,
            'journal_id': self.journal_id.id,
            'partner_id': self.partner_id.id,
            'currency_id': company_currency != current_currency and current_currency or False,
            'amount_currency': (sign * abs(self.amount)  # amount < 0 for refunds
                                if company_currency != current_currency else 0.0),
            'date': self.account_date,
            'date_maturity': self.date_due
        }
        return move_line

    @api.multi
    def account_move_get(self):
        if self.number:
            name = self.number
        else:
            from datetime import datetime
            date_here = datetime.strptime(self.date, '%Y-%m-%d %H:%M:%S')
            sequence = self.env['ir.sequence'].with_context(ir_sequence_date=str(date_here.date())). \
                next_by_code(SEQ_TYPE.get(self.voucher_type))
            name = sequence if sequence else ''

        move = {
            'name': name,
            'journal_id': self.journal_id.id,
            'narration': self.narration,
            'date': self.account_date,
            'ref': self.reference,
        }
        return move

    @api.multi
    def _convert_amount(self, amount):
        '''
        This function convert the amount given in company currency. It takes either the rate in the voucher (if the
        payment_rate_currency_id is relevant) either the rate encoded in the system.
        :param amount: float. The amount to convert
        :param voucher: id of the voucher on which we want the conversion
        :param context: to context to use for the conversion. It may contain the key 'date' set to the voucher date
            field in order to select the good rate to use.
        :return: the amount in the currency of the voucher's company
        :rtype: float
        '''
        for voucher in self:
            return voucher.currency_id.compute(amount, voucher.company_id.currency_id)

    @api.multi
    def voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
        for line in self.line_ids:
            # create one move line per voucher line where amount is not 0.0
            if not line.price_subtotal:
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context,
            # so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(line.price_unit * line.quantity)
            move_line = {
                'journal_id': self.journal_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': self.partner_id.id,
                'cost_center_id': line.cost_center_id and line.cost_center_id.id or False,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': abs(amount) if self.voucher_type == 'sale' else 0.0,
                'debit': abs(amount) if self.voucher_type == 'purchase' else 0.0,
                'date': self.account_date,
                'tax_ids': [(4, t.id) for t in line.tax_ids],
                'amount_currency': line.price_subtotal if current_currency != company_currency else 0.0,
                'currency_id': company_currency != current_currency and current_currency or False,
            }

            self.env['account.move.line'].with_context(apply_taxes=True).create(move_line)
        return line_total

    @api.multi
    def action_move_line_create(self):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        for voucher in self:
            local_context = dict(self._context, force_company=voucher.journal_id.company_id.id)
            if voucher.move_id:
                continue
            amount = self.amount
            sum_price_subtotal = 0.0
            for line in self.line_ids:
                amount -= line.price_subtotal
                sum_price_subtotal += line.price_subtotal
            # if amount != 0.0:
            # if sum_price_subtotal != self.amount :
            #     raise UserError('Please Validate the Payment Lines. Total Amount and'
            #                     'Sum of lines doesnt match')
            company_currency = voucher.journal_id.company_id.currency_id.id
            current_currency = voucher.currency_id.id or company_currency
            # we select the context to use accordingly if it's a multicurrency case or not
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = local_context.copy()
            ctx['date'] = voucher.account_date
            ctx['check_move_validity'] = False
            # Create the account move record.
            move = self.env['account.move'].create(voucher.account_move_get())
            # Get the name of the account_move just created
            # Create the first line of the voucher with main Asset/Payable Account (Cash, Bank, etc)
            move_line = self.env['account.move.line'].with_context(ctx).create(voucher.with_context(ctx).first_move_line_get(move.id, company_currency, current_currency))
            line_total = move_line.debit - move_line.credit
            if voucher.voucher_type == 'sale':
                line_total = line_total - voucher._convert_amount(voucher.tax_amount)
            elif voucher.voucher_type == 'purchase':
                line_total = line_total + voucher._convert_amount(voucher.tax_amount)
            # Create one move line per voucher line where amount is not 0.0
            line_total = voucher.with_context(ctx).voucher_move_line_create(line_total, move.id, company_currency, current_currency)

            # Add tax correction to move line if any tax correction specified
            if voucher.tax_correction != 0.0:
                tax_move_line = self.env['account.move.line'].search(
                    [('move_id', '=', move.id), ('tax_line_id', '!=', False)], limit=1)
                if len(tax_move_line):
                    tax_move_line.write({'debit': tax_move_line.debit + voucher.tax_correction if tax_move_line.debit > 0 else 0,
                         'credit': tax_move_line.credit + voucher.tax_correction if tax_move_line.credit > 0 else 0})

            # We post the voucher.
            voucher.write({
                'move_id': move.id,
                'state': 'posted',
                'number': move.name
            })
            move.post()
        return True


class AccountVoucherLine(models.Model):
    _name = 'account.voucher.line'
    _description = 'Voucher Lines'

    name = fields.Text(string='Description')
    sequence = fields.Integer(default=10,
                              help="Gives the sequence of this line when displaying the voucher.")
    voucher_id = fields.Many2one('account.voucher', 'Voucher', required=1, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product',
                                 ondelete='set null', index=True)
    cost_center_id = fields.Many2one('account.cost.center', string='Cost Center', index=True)

    date = fields.Datetime("Bill Date", related='voucher_id.date')

    def _compute_balance_after_trans(self):
        for voucher_line in self:
            prev_move_line = self.env['account.move.line'].search([('account_id', '=', voucher_line.account_id.id),
                                                                   ('date', '<=',  voucher_line.date),
                                                                   ('move_id.state', '=', 'posted'),
                                                                   ])
            total_debit = 0.0
            total_credit = 0.0
            for move_line in prev_move_line:
                total_debit = total_debit + move_line.debit
                total_credit = total_credit + move_line.credit
            voucher_line.balance_after_trans = total_debit - total_credit

    balance_after_trans = fields.Monetary(string='Balance', readonly=True, compute='_compute_balance_after_trans')
    account_id = fields.Many2one('account.account', string='Account',
                                 required=True, domain=[('deprecated', '=', False)],
                                 help="The income or expense account related to the selected product.")
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'),
                              oldname='amount')
    price_subtotal = fields.Monetary(string='Amount',
                                     store=True, compute='_compute_subtotal')
    quantity = fields.Float(digits=dp.get_precision('Product Unit of Measure'),
                            required=True, default=1)
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    company_id = fields.Many2one('res.company', related='voucher_id.company_id', string='Company', store=True,
                                 readonly=True)
    tax_ids = fields.Many2many('account.tax', string='Tax', help="Only for tax excluded from price")
    currency_id = fields.Many2one('res.currency', related='voucher_id.currency_id')

    @api.depends('price_unit', 'tax_ids', 'quantity', 'product_id', 'voucher_id.currency_id')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
            if line.tax_ids:
                taxes = line.tax_ids.compute_all(line.price_unit, line.voucher_id.currency_id, line.quantity, product=line.product_id, partner=line.voucher_id.partner_id)
                line.price_subtotal = taxes['total_excluded']

    @api.onchange('product_id', 'price_unit')
    def _onchange_line_details(self):
        if not self.product_id:
            return {}
        context = self.env.context
        company = self.company_id if self.company_id is not None else context.get('company_id', False)
        currency = self.currency_id
        if not self.voucher_id.partner_id:
            raise UserError(_("You must first select a partner!"))
        if self.voucher_id.partner_id.lang:
            self = self.with_context(lang=self.voucher_id.partner_id.lang)

        fpos = self.voucher_id.partner_id.property_account_position_id
        accounts = self.product_id.product_tmpl_id.get_product_accounts(fpos)
        account = accounts['income'] if type == 'sale' else accounts['expense']
        values = {
            'name': self.product_id.partner_ref,
            'account_id': account.id,
        }
        if type == 'purchase':
            values['price_unit'] = self.price_unit or self.product_id.standard_price
            taxes = self.product_id.supplier_taxes_id or account.tax_ids
            if self.product_id.description_purchase:
                values['name'] += '\n' + self.product_id.description_purchase
        else:
            values['price_unit'] = self.product_id.lst_price
            taxes = self.product_id.taxes_id or account.tax_ids
            if self.product_id.description_sale:
                values['name'] += '\n' + self.product_id.description_sale

        values['tax_ids'] = taxes.ids

        if company and currency:
            if company.currency_id != currency:
                if type == 'purchase':
                    values['price_unit'] = self.product_id.standard_price
                values['price_unit'] = values['price_unit'] * currency.rate
        return {'value': values}
