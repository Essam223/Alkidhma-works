# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from ast import literal_eval


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.onchange('partner_id')
    def check_partner_kk(self):
        self.set_access_to_edit_discount()

    def set_access_to_edit_discount(self):
        for rec in self:
            if self.env.user.has_group('sale.group_discount_per_so_line') and rec.state == 'draft':
                rec.access_to_edit_discount = True

    access_to_edit_discount = fields.Boolean(compute=set_access_to_edit_discount, string='Edit Invoice Discount?')

    @api.multi
    @api.returns('self')
    def refund(self, date_invoice=None, date=None, description=None, journal_id=None):
        res = super(AccountInvoice, self).refund(date_invoice, date, description, journal_id)
        res.update({
            'discount_fixed_percent': self.discount_fixed_percent,
            'discount': self.discount,
            'discount_value': self.discount_value,
        })
        return res

    @api.model
    def _get_payments_vals(self):
        res = super(AccountInvoice, self)._get_payments_vals()
        for i in  res:
            i['salesperson'] = False
            payment = i.get('account_payment_id')
            if payment:
                i['salesperson'] = self.env['account.payment'].browse(payment).create_uid.name
            i['date_new'] = False
            if i.get('date'):
                i['date_new'] = i.get('date').split(" ")[0]
        return res

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.with_context(ctx).write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or '/'
            disc_amount_final = 0.0
            total_disc_amount_final = total
            if inv.discount_fixed_percent:
                if inv.discount_fixed_percent == 'Percent':
                    self_amount_total = inv.amount_untaxed + inv.amount_tax
                    disc_amount_final = self_amount_total * (inv.discount / 100.0)
                if inv.discount_fixed_percent == 'Fixed':
                    disc_amount_final = inv.discount_value
                ICPSudo = self.env['ir.config_parameter'].sudo()
                default_discount_account = literal_eval(ICPSudo.get_param('default_discount_account', default='False'))
                if not default_discount_account:
                    raise UserError(_('Please define Discount Account in Accounting Configuration.'))
                company_currency = inv.company_id.currency_id
                diff_currency = inv.currency_id != company_currency
                inv_bill_cred = ('out_invoice', 'in_refund')
                bill_inv_credit = ('in_invoice', 'out_refund')
                if inv.type in inv_bill_cred:
                    type_here = 'dest'
                    total_disc_amount_final = total-disc_amount_final
                if inv.type in bill_inv_credit:
                    type_here = 'src'
                    total_disc_amount_final = total + disc_amount_final
                    disc_amount_final = -disc_amount_final
                iml.append({
                    'type': type_here,
                    'name': 'GLOBAL DISCOUNT',
                    'price': disc_amount_final,
                    'account_id': default_discount_account,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id,
                    'partner_id': inv.partner_id.id,
                })
            if inv.payment_term_id:
                totlines = \
                inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total,
                                                                                                            inv.date_invoice)[
                    0]
                res_amount_currency = total_currency
                ctx['date'] = inv.date or inv.date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total_disc_amount_final,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
        return True

    discount_fixed_percent = fields.Selection([('Fixed', 'Fixed'), ('Percent', 'Percent')],
                                              string='Disc Fixed/Percent', default=False, track_visibility='always',
                                              readonly=True, states={'draft': [('readonly', False)]})
    discount = fields.Float(string='Disc (%)', digits=dp.get_precision('Discount'), default=0.0,
                            track_visibility='always', readonly=True, states={'draft': [('readonly', False)]})
    discount_value = fields.Float(string='Disc Amt', track_visibility='always', readonly=True,
                                  states={'draft': [('readonly', False)]})

    @api.onchange('discount', 'discount_value')
    def _onchange_discount_value(self):
        if self.discount_fixed_percent == 'Fixed':
            if self.discount_value > self.amount_untaxed + self.amount_tax:
                raise UserError(_('Discount Amount should not be greater than Total Amount.'))
        if self.discount_fixed_percent == 'Percent':
            if self.discount > 100:
                raise UserError(_('Discount Percentage should not be greater than 100'))

    @api.onchange('discount_fixed_percent')
    def _onchange_discount_fixed_percent(self):
        if not self.discount_fixed_percent:
            self.discount = ""
            self.discount_value = ""
        if self.discount_fixed_percent == 'Fixed':
            self.discount = ""
        if self.discount_fixed_percent == 'Percent':
            self.discount_value = ""

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type', 'discount_fixed_percent', 'discount', 'discount_value')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount_total for line in self.tax_line_ids)
        self.amount_before_disc = self.amount_untaxed + self.amount_tax
        self_amount_total = self.amount_untaxed + self.amount_tax
        if not self.discount_fixed_percent:
            self.amount_total = self_amount_total
        if self.discount_fixed_percent == 'Percent':
            self.amount_total = self_amount_total * (1 - (self.discount or 0.0) / 100.0)
        if self.discount_fixed_percent == 'Fixed':
            self.amount_total = self_amount_total - self.discount_value
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    amount_before_disc = fields.Monetary(string='Before Disc', store=True, readonly=True, compute='_compute_amount',
                                         track_visibility='always')


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    @api.onchange('product_id')
    def check_product_kk(self):
        self.set_access_to_edit_discount()

    def set_access_to_edit_discount(self):
        for rec in self:
            if self.env.user.has_group('sale.group_discount_per_so_line'):
                rec.access_to_edit_discount = True

    access_to_edit_discount = fields.Boolean(compute=set_access_to_edit_discount,  string='Edit Invoice line Discount?')
    discount_fixed_percent = fields.Selection([('Fixed', 'Fixed'), ('Percent', 'Percent')],
                                              string='Disc Fixed/Percent', default=False)
    discount = fields.Float(string='Disc (%)', digits=dp.get_precision('Discount'), default=0.0)
    discount_value = fields.Float(string='Disc Amt')

    @api.onchange('discount', 'discount_value')
    def _onchange_discount_value(self):
        if self.discount_fixed_percent == 'Fixed':
            if self.discount_value > self.price_unit:
                raise UserError(_('Discount Amount should not be greater than Total Amount.'))
        if self.discount_fixed_percent == 'Percent':
            if self.discount > 100:
                raise UserError(_('Discount Percentage should not be greater than 100'))

    @api.onchange('discount_fixed_percent')
    def _onchange_discount_fixed_percent(self):
        if not self.discount_fixed_percent:
            self.discount = ""
            self.discount_value = ""
        if self.discount_fixed_percent == 'Fixed':
            self.discount = ""
        if self.discount_fixed_percent == 'Percent':
            self.discount_value = ""

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'invoice_id.date', 'discount_fixed_percent', 'discount_value')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                          partner=self.invoice_id.partner_id)
        self_price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        if not self.discount_fixed_percent:
            self_price_subtotal = self_price_subtotal
        if self.discount_fixed_percent == 'Percent':
            self_price_subtotal = self_price_subtotal * (1 - (self.discount or 0.0) / 100.0)
        if self.discount_fixed_percent == 'Fixed':
            self_price_subtotal = self_price_subtotal - self.discount_value
        self.price_subtotal = self_price_subtotal
        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(
                price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
