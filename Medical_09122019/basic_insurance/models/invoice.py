# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError
from ast import literal_eval


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    insurance_share = fields.Float('Insurance Share', readonly=True, states={'draft': [('readonly', False)]},
                                   track_visibility='always')
    patient_share = fields.Float('Patient Share', readonly=True, states={'draft': [('readonly', False)]},
                                 track_visibility='always')
    after_treatment_grp_disc = fields.Float('After Treatment group discount', readonly=True,
                                            states={'draft': [('readonly', False)]}, track_visibility='always')
    share_based_on = fields.Selection([('Global', 'Global'), ('Treatment', 'Treatment line')],
                                      'Insurance based on', required=False,readonly=True,
                                      states={'draft': [('readonly', False)]}, track_visibility='always')

    @api.onchange('insurance_share')
    def onchange_share_ins(self):
        if self.is_patient and self.insurance_card and self.insurance_company and not self.discount_fixed_percent:
            if self.share_based_on == 'Global':
                if self.insurance_share > self.net_amount:
                    self.patient_share = 0.0
                    self.insurance_share = 0.0
                if self.insurance_share:
                    self.patient_share = self.net_amount - self.insurance_share
                    self.insurance_total = self.insurance_share

    @api.onchange('patient_share')
    def onchange_share_pat(self):
        if self.is_patient and self.insurance_card and self.insurance_company and not self.discount_fixed_percent:
            if self.share_based_on == 'Global':
                if self.patient_share > self.net_amount:
                    self.patient_share = 0.0
                    self.insurance_share = 0.0
                if self.patient_share:
                    self.insurance_share = self.net_amount - self.patient_share
                    self.amount_total = self.patient_share

    @api.onchange('after_treatment_grp_disc')
    def onchange_after_treatment_grp_disc(self):
        if self.is_patient and self.insurance_card and self.insurance_company and not self.discount_fixed_percent:
            if self.share_based_on == 'Global':
                self.patient_share = 0.0
                self.insurance_share = 0.0
                if self.after_treatment_grp_disc > self.amount_subtotal:
                    self.after_treatment_grp_disc = 0.0

    @api.onchange('share_based_on')
    def onchange_share_based_on(self):
        if self.share_based_on == 'Global':
            for line in self.invoice_line_ids:
                line.insurance_share = 0.0
                line.patient_share = 0.0
                line.after_treatment_grp_disc = 0.0
        if self.share_based_on == 'Treatment':
            self.patient_share = 0.0
            self.insurance_share = 0.0
            self.after_treatment_grp_disc = 0.0
            for line in self.invoice_line_ids:
                non_coverage_companies = [ins_company.id for ins_company in line.product_id.non_coverage_insurance_company_ids]
                if self.insurance_company.id in non_coverage_companies:
                    line.patient_share = line.quantity * line.price_unit
                    line.after_treatment_grp_disc = line.quantity * line.price_unit
                    # line.patient_share = line.price_subtotal
                    # line.after_treatment_grp_disc = line.price_subtotal

    def get_after_treatment_grp_disc_amt(self):
        total_after_treatment_grp_disc = 0.0
        if self.share_based_on == 'Global':
            total_after_treatment_grp_disc = self.after_treatment_grp_disc
        if self.share_based_on == 'Treatment':
            for line in self.invoice_line_ids:
                total_after_treatment_grp_disc += line.after_treatment_grp_disc
        return total_after_treatment_grp_disc

    def get_patient_insurance_amt(self):
        total_insurance_share = 0.0
        total_patient_share = 0.0
        if self.share_based_on == 'Global':
            total_patient_share = self.patient_share
            total_insurance_share = self.insurance_share
        if self.share_based_on == 'Treatment':
            for line in self.invoice_line_ids:
                total_insurance_share += line.insurance_share
                total_patient_share += line.patient_share
        return total_insurance_share, total_patient_share

    @api.onchange('insurance_card')
    @api.depends('insurance_card')
    def onchange_insurance_company(self):
        self.ins_approved_amt = 0.0
        self.insurance_company = self.insurance_card.company_id.id
        for line in self.invoice_line_ids:
            if line.apply_insurance:
                if self.insurance_card.co_payment_method == 'Percentage':
                    line.amt_fixed_paid_by_patient = 0.0
                    if line.insurance_cases == 'case_1':
                        line.amt_paid_by_patient = self.insurance_company.amt_paid_by_patient
                        line.amt_paid_by_insurance = self.insurance_company.amt_paid_by_insurance
                    if line.insurance_cases in ('case_3', 'case_2'):
                        line.amt_paid_by_patient = self.insurance_card.amt_paid_by_patient
                        line.amt_paid_by_insurance = 100 - self.insurance_card.amt_paid_by_patient
                if self.insurance_card.co_payment_method == 'Amount':
                    line.amt_fixed_paid_by_patient = self.insurance_card.amt_fixed_paid_by_patient
                    line.amt_paid_by_patient = 0.0
                    line.amt_paid_by_insurance = 0.0
                line.insurance_cases = self.insurance_company.insurance_cases
                line.discount_amt = self.insurance_company.discount_amt
                if line.insurance_cases == 'case_2':
                    line.discount_amt = line.product_id.discount_amt
            else:
                if self.insurance_card.co_payment_method == 'Percentage':
                    line.amt_paid_by_patient = 100
                    line.amt_paid_by_insurance = 0.0
                if self.insurance_card.co_payment_method == 'Amount':
                    line.amt_paid_by_patient = 0.0
                    line.amt_paid_by_insurance = 0.0

    @api.depends('invoice_line_ids', 'invoice_line_ids.insurance_share', 'invoice_line_ids.price_subtotal', 'invoice_line_ids.amt_paid_by_insurance',
                 'ins_approved_amt', 'consult_approved_amt', 'share_based_on', 'insurance_share', 'patient_share',
                 'insurance_company', 'insurance_card', 'after_treatment_grp_disc')
    def _compute_insurance_total(self):
        for record in self:
            if record.insurance_company:
                total_insurance_share, total_patient_share = self.get_patient_insurance_amt()
                total_after_treatment_grp_disc = self.get_after_treatment_grp_disc_amt()
                record.insurance_total = total_insurance_share
                # qty_price_unit_total = 0
                # treatment_group_disc_total = 0
                # for line in record.invoice_line_ids:
                #     qty_price_unit_total += (line.price_unit * line.quantity)
                #     if line.apply_insurance:
                #         if line.insurance_cases == 'case_1':
                #             treatment_total = (line.price_unit * line.quantity * line.discount_amt) / 100
                #             treatment_group_disc_total += treatment_total
                #         if line.insurance_cases in ('case_3', 'case_2'):
                #             treatment_total = (line.price_unit * line.quantity * line.discount_amt) / 100
                #             treatment_group_disc_total += treatment_total
                # record.net_amount = qty_price_unit_total - treatment_group_disc_total
                record.net_amount = total_after_treatment_grp_disc
                # record.treatment_group_disc_total = treatment_group_disc_total
                record.treatment_group_disc_total = record.amount_subtotal - total_after_treatment_grp_disc
            else:
                record.insurance_total = 0.0
                record.net_amount = 0.0
                record.treatment_group_disc_total = 0.0
            record.patient_copayment_total = 0.0
            record.is_treatment = False
            record.is_consultation = False
            record.initial_patient_copayment = 0.0
            record.consultation_net_amt = 0.0
            record.initial_insurance = 0.0

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type', 'discount_fixed_percent', 'discount',
                 'discount_value', 'share_based_on', 'insurance_share', 'patient_share', 'insurance_company',
                 'insurance_card', 'after_treatment_grp_disc')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount_total for line in self.tax_line_ids)
        self.amount_before_disc = self.amount_untaxed + self.amount_tax
        self_amount_total = 0.0
        if self.is_patient and self.patient and self.insurance_card and self.insurance_company:
            if self.share_based_on:
                total_insurance_share, total_patient_share = self.get_patient_insurance_amt()
                self_amount_total = total_patient_share
        elif self.is_insurance_company:
            patient_invoice = self.search([('insurance_invoice', '=', self.id)], limit=1)
            self_amount_total = patient_invoice.insurance_total
        else:
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

    @api.multi
    def modify_invoice(self):
        if self.is_patient and self.insurance_invoice:
            self.insurance_invoice.action_invoice_cancel()
        self.write({'insurance_invoice': False})
        res = super(AccountInvoice, self).modify_invoice()
        return res

    @api.multi
    def action_invoice_open_new(self):
        if self.is_patient and self.insurance_card and self.insurance_company and not self.discount_fixed_percent:
            if self.net_amount != self.insurance_total+ self.amount_total:
                raise UserError(_('Please enter insurance company share and patient share properly.'))
        res = super(AccountInvoice, self).action_invoice_open_new()
        return res

    @api.multi
    def action_invoice_open(self):
        if self.is_patient and self.insurance_card and self.insurance_company and not self.discount_fixed_percent:
            if self.net_amount != self.insurance_total + self.amount_total:
                raise UserError(_('Please enter insurance company share and patient share properly.'))
        res = super(AccountInvoice, self).action_invoice_open()
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
            if inv.consult_approved_amt and not inv.share_based_on:
                for lines in iml:
                    product_id = self.env['product.product'].browse(lines['product_id'])
                    consultation_companies = [ins_company.id for ins_company in
                                              product_id.consultation_insurance_company_ids]
                    if inv.insurance_company.id == inv.insurance_card.company_id.id and \
                                    inv.insurance_company.id in consultation_companies:
                        lines['price_unit'] = inv.consult_approved_amt
                        lines['price'] = inv.consult_approved_amt

            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or '/'
            disc_amount_final = 0.0
            total_disc_amount_final = total
            inv_bill_cred = ('out_invoice', 'in_refund')
            bill_inv_credit = ('in_invoice', 'out_refund')
            if inv.is_patient and inv.share_based_on == 'Global':
                for line in inv.invoice_line_ids:
                    sale_account_id = line.account_id
                if sale_account_id:
                    Insurance_treatment_dict = {
                        'type': 'dest',
                        'name': 'After Treatment Group Discount',
                        'price': -inv.after_treatment_grp_disc,
                        'account_id': sale_account_id.id,
                        'cost_center_id': inv.cost_center_id.id,
                        'company_id': inv.company_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    }
                    iml.append(Insurance_treatment_dict)
            if inv.discount_fixed_percent:
                if inv.discount_fixed_percent == 'Percent':
                    self_amount_total = inv.amount_untaxed + inv.amount_tax
                    disc_amount_final = self_amount_total * (inv.discount / 100.0)
                if inv.discount_fixed_percent == 'Fixed':
                    disc_amount_final = inv.discount_value
                ICPSudo = self.env['ir.config_parameter'].sudo()
                if not self.env.user.has_group('base.group_multi_company'):
                    default_discount_account = literal_eval(ICPSudo.get_param('default_discount_account', default='False'))
                    if not default_discount_account:
                        raise UserError(_('Please define Discount Account in Accounting Configuration.'))
                else:
                    default_discount_account = inv.company_id.default_discount_account.id
                    if not default_discount_account:
                        raise UserError(_('Please define Discount Account in Company Configuration.'))
                company_currency = inv.company_id.currency_id
                diff_currency = inv.currency_id != company_currency
                if inv.type in inv_bill_cred:
                    type_here = 'dest'
                    total_disc_amount_final = total - disc_amount_final
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
                ICPSudo = self.env['ir.config_parameter'].sudo()
                if not self.env.user.has_group('base.group_multi_company'):
                    default_insurance_diff_account = literal_eval(ICPSudo.get_param('default_insurance_diff_account', default='False'))
                    if not default_insurance_diff_account:
                        raise UserError(_('Please define Insurance Difference Account in Accounting Configuration.'))
                else:
                    default_insurance_diff_account = inv.company_id.default_insurance_diff_account.id
                    if not default_insurance_diff_account:
                        raise UserError(_('Please define Insurance Difference Account in Company Configuration.'))
                if inv.is_patient:
                    total_disc_amount_final -= inv.insurance_total
                    if inv.insurance_total:
                        Insurance_line_dict = {
                            'type': 'src',
                            'name': 'Insurance Difference',
                            'price': inv.insurance_total,
                            'account_id': default_insurance_diff_account,
                            'date_maturity': inv.date_due,
                            'amount_currency': diff_currency and total_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        }
                        iml.append(Insurance_line_dict)
                if inv.is_insurance_company:
                    patient_invoice = self.search([('insurance_invoice', '=', inv.id)], limit=1)
                    total_disc_amount_final += patient_invoice.insurance_total
                    if patient_invoice.insurance_total:
                        Insurance_line_dict = {
                            'type': 'src',
                            'name': 'Insurance Difference',
                            'price': -patient_invoice.insurance_total,
                            'account_id': default_insurance_diff_account,
                            'date_maturity': inv.date_due,
                            'amount_currency': diff_currency and total_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        }
                        iml.append(Insurance_line_dict)
                if inv.type in inv_bill_cred:
                    type_here = 'dest'
                    inv_amount_total = inv.amount_total
                if inv.type in bill_inv_credit:
                    type_here = 'src'
                    inv_amount_total = -inv.amount_total
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': inv_amount_total,
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

    def show_insurance_inv_line(self, inv_line):
        treatment_companies = [ins_company.id for ins_company in inv_line.product_id.insurance_company_ids]
        consultation_companies = [ins_company.id for ins_company in inv_line.product_id.consultation_insurance_company_ids]
        if self.insurance_company.id in treatment_companies or self.insurance_company.id in consultation_companies:
            return True
        return False

    def patient_invoice_validate(self):
        if self.insurance_company and self.insurance_total > 0:
            invoice_line_ids = self.invoice_line_ids
            invoice_vals = {}
            invoice_line_vals = []
            insurance_company = self.insurance_company
            # Creating invoice lines
            # get account id for products
            jr_brw = self.env['account.journal'].search([('type', '=', 'sale'), ('name', '=', 'Customer Invoices'), ('company_id', '=', self.company_id.id)])
            for each in invoice_line_ids:
                if self.insurance_company.id == self.insurance_card.company_id.id:
                    if self.show_insurance_inv_line(each):
                        each_line = [0, False]
                        product_dict = {}
                        product_dict['product_id'] = each.product_id.id
                        product_dict['amt_paid_by_patient'] = 0
                        product_dict['discount_amt'] = 0
                        product_dict['amt_paid_by_insurance'] = 0
                        product_dict['insurance_cases'] = False
                        product_dict['name'] = each.name
                        product_dict['quantity'] = each.quantity
                        product_dict['price_unit'] = 0.0
                        acc_obj = self.env['account.account'].search([('name', '=', 'Local Sales'),
                                                                      ('user_type_id', '=', 'Income')], limit=1)
                        for account_id in jr_brw:
                            product_dict[
                                'account_id'] = account_id.default_debit_account_id.id if account_id.default_debit_account_id else acc_obj.id
                        each_line.append(product_dict)
                        invoice_line_vals.append(each_line)
                # Creating invoice dictionary
            invoice_vals['account_id'] = insurance_company.property_account_receivable_id.id
            invoice_vals['company_id'] = self.company_id.id
            invoice_vals['journal_id'] = jr_brw.id
            invoice_vals['partner_id'] = insurance_company.id
            invoice_vals['dentist'] = self.dentist.id
            invoice_vals['is_insurance_company'] = True
            if self.appt_id.id:
                invoice_vals['appt_id'] = self.appt_id.id
            invoice_vals['insurance_company'] = False
            invoice_vals['insurance_card'] = False
            invoice_vals['invoice_line_ids'] = invoice_line_vals
            if invoice_vals:
                inv_id = self.env['account.invoice'].create(invoice_vals)
                self.write({'insurance_invoice': inv_id.id})
                if self.patient:
                    inv_id.write({'patient':self.patient.id})
                inv_id.action_invoice_open()


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('amt_paid_by_patient', 'amt_paid_by_insurance', 'discount_amt', 'invoice_id.insurance_company',
                 'price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'invoice_id.date', 'discount_fixed_percent', 'discount',
                 'discount_value', 'after_treatment_grp_disc', 'share_based_on')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                          partner=self.invoice_id.partner_id)
        treatment_companies = [ins_company.id for ins_company in self.product_id.insurance_company_ids]
        patient_companies = [insurance.company_id.id for insurance in self.partner_id.insurance_ids]
        self_price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        if self.invoice_id.insurance_company.id in treatment_companies and self.invoice_id.insurance_company.id in patient_companies:
            if self.insurance_cases == 'case_1':
                treatment_total = (self.price_unit * self.quantity * self.discount_amt) / 100
                total_payable = self.price_unit * self.quantity - treatment_total
                self_price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else total_payable
            if self.insurance_cases in ('case_3', 'case_2'):
                treatment_total = (self.price_unit * self.quantity * self.discount_amt) / 100
                total_payable = self.price_unit * self.quantity - treatment_total
                self_price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else total_payable
        if self.invoice_id.share_based_on == 'Treatment':
            self_price_subtotal = self.after_treatment_grp_disc
        if self.invoice_id.share_based_on == 'Global':
            self_price_subtotal = 0.0
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
        self.price_initial_copay = 0.0

    insurance_share = fields.Float('Insurance Share')
    patient_share = fields.Float('Patient Share')
    after_treatment_grp_disc = fields.Float('After Treatment group discount')
    share_based_on = fields.Selection([('Global', 'Global'), ('Treatment', 'Treatment line')],
                                      'Insurance based on', required=False, related='invoice_id.share_based_on')

    @api.onchange('insurance_share')
    def onchange_line_share_ins(self):
        if self.invoice_id.is_patient and self.invoice_id.insurance_card and self.invoice_id.insurance_company:
            if self.share_based_on == 'Treatment':
                if self.insurance_share > self.price_subtotal:
                    self.patient_share = 0.0
                    self.insurance_share = 0.0
                if self.after_treatment_grp_disc and self.insurance_share:
                    self.patient_share = self.after_treatment_grp_disc - self.insurance_share

    @api.onchange('patient_share')
    def onchange_line_share_pat(self):
        if self.invoice_id.is_patient and self.invoice_id.insurance_card and self.invoice_id.insurance_company:
            if self.share_based_on == 'Treatment':
                if self.patient_share > self.price_subtotal:
                    self.patient_share = 0.0
                    self.insurance_share = 0.0
                if self.patient_share and self.after_treatment_grp_disc:
                    self.insurance_share = self.after_treatment_grp_disc - self.patient_share

    @api.onchange('after_treatment_grp_disc')
    def onchange_line_after_treatment_grp_disc(self):
        if self.invoice_id.is_patient and self.invoice_id.insurance_card and self.invoice_id.insurance_company:
            if self.share_based_on == 'Treatment':
                self.patient_share = 0.0
                self.insurance_share = 0.0
                if self.after_treatment_grp_disc > (self.price_unit * self.quantity):
                    self.after_treatment_grp_disc = 0.0
