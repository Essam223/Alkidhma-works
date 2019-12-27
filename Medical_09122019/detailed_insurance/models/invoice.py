# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError
from ast import literal_eval


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    is_special_case = fields.Boolean('Is Special case', readonly=True, states={'draft': [('readonly', False)]},
                                     track_visibility='always')

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        params = self.env.context.get('params', False)
        if params:
            order_id = params.get('id', False)
            if order_id:
                order_record = self.browse(order_id)
                if order_record:
                    if order_record.is_patient and order_record.insurance_card and order_record.is_special_case:
                        self = self.with_context(amt_paid_by_patient_edit_invisible=False)
        return super(AccountInvoice, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                           submenu=submenu)

    @api.multi
    def action_invoice_open_new(self):
        if self.is_patient and self.insurance_card and self.insurance_company and not self.discount_fixed_percent and \
                self.is_special_case:
            if self.share_based_on == 'Global':
                if self.net_amount != self.after_treatment_grp_disc or self.after_treatment_grp_disc > self.amount_subtotal:
                    raise UserError(_('Please enter After Treatment group discount properly.'))
            if self.share_based_on == 'Treatment':
                if self.after_treatment_grp_disc > self.amount_subtotal:
                    raise UserError(_('Please enter After Treatment group discount properly.'))
        res = super(AccountInvoice, self).action_invoice_open_new()
        return res

    @api.multi
    def action_invoice_open(self):
        if self.is_patient and self.insurance_card and self.insurance_company and not self.discount_fixed_percent and \
                self.is_special_case:
            if self.share_based_on == 'Global':
                if self.net_amount != self.after_treatment_grp_disc or self.after_treatment_grp_disc > self.amount_subtotal:
                    raise UserError(_('Please enter After Treatment group discount properly.'))
            if self.share_based_on == 'Treatment':
                if self.after_treatment_grp_disc > self.amount_subtotal:
                    raise UserError(_('Please enter After Treatment group discount properly.'))
        res = super(AccountInvoice, self).action_invoice_open()
        return res

    def show_insurance_inv_line(self, inv_line):
        if self.is_special_case:
            return True
        else:
            treatment_companies = [ins_company.id for ins_company in inv_line.product_id.insurance_company_ids]
            consultation_companies = [ins_company.id for ins_company in inv_line.product_id.consultation_insurance_company_ids]
            if self.insurance_company.id in treatment_companies or self.insurance_company.id in consultation_companies:
                return True
        return False

    @api.onchange('is_special_case')
    def onchange_is_special_case(self):
        if self.is_special_case:
            self.share_based_on = 'Global'
        if not self.is_special_case:
            self.share_based_on = False
            self.insurance_share = 0.0
            self.patient_share = 0.0
            self.after_treatment_grp_disc = 0.0
            for line in self.invoice_line_ids:
                line.insurance_share = 0.0
                line.patient_share = 0.0
                line.after_treatment_grp_disc = 0.0

    @api.depends('invoice_line_ids', 'invoice_line_ids.price_subtotal', 'invoice_line_ids.amt_paid_by_insurance',
                 'ins_approved_amt', 'consult_approved_amt', 'is_special_case', 'share_based_on', 'insurance_share',
                 'patient_share', 'insurance_company', 'insurance_card', 'after_treatment_grp_disc')
    def _compute_insurance_total(self):
        for record in self:
            record.is_treatment = False
            record.is_consultation = False
            if record.insurance_company:
                qty_price_unit_total = 0
                treatment_group_disc_total = 0
                for line in record.invoice_line_ids:
                    item_total = (line.price_unit * line.quantity)
                    if line.discount_fixed_percent == 'Percent':
                        item_total = item_total * (1 - (line.discount or 0.0) / 100.0)
                    if line.discount_fixed_percent == 'Fixed':
                        item_total = item_total - line.discount_value
                    qty_price_unit_total += item_total
                    if line.apply_insurance:
                        if line.insurance_cases in ('case_1', 'case_3', 'case_2'):
                            treatment_total = (item_total * line.discount_amt) / 100
                            treatment_group_disc_total += treatment_total
                record.net_amount = qty_price_unit_total - treatment_group_disc_total
                record.treatment_group_disc_total = treatment_group_disc_total
                if record.is_special_case:
                    total_insurance_share, total_patient_share = record.get_patient_insurance_amt()
                    total_after_treatment_grp_disc = record.get_after_treatment_grp_disc_amt()
                    record.net_amount = total_after_treatment_grp_disc
                    record.insurance_total = total_insurance_share
                    record.patient_copayment_total = 0.0
                    record.is_treatment = False
                    record.is_consultation = False
                    record.initial_patient_copayment = 0.0
                    record.consultation_net_amt = 0.0
                    record.initial_insurance = 0.0
                else:
                    ins_total = 0
                    consultation_net_amt = 0
                    patient_copayment = 0
                    tot_ins_approved_amt = 0.0
                    tot_consult_approved_amt = 0.0
                    consultation_original_amt = 0.0
                    is_consultation = 0
                    is_treatment = 0
                    for line in record.invoice_line_ids:
                        if line.apply_insurance:
                            is_treatment = 1
                            item_total = (line.price_unit * line.quantity)
                            if line.discount_fixed_percent == 'Percent':
                                item_total = item_total * (1 - (line.discount or 0.0) / 100.0)
                            if line.discount_fixed_percent == 'Fixed':
                                item_total = item_total - line.discount_value

                            if line.insurance_cases == 'case_1':
                                treatment_total = (item_total * line.discount_amt) / 100
                                ins_total += (item_total * line.amt_paid_by_insurance) / 100
                            if line.insurance_cases in ('case_3', 'case_2'):
                                treatment_total = (item_total * line.discount_amt) / 100
                                total_payable = item_total - treatment_total
                                ins_total += (total_payable * line.amt_paid_by_insurance) / 100
                            if record.insurance_company.approved_amt_based_on == 'after_treatment_grp_disc':
                                tot_ins_approved_amt += line.price_subtotal
                            if record.insurance_company.approved_amt_based_on == 'gross_amount':
                                qty_price_unit_total = (line.price_unit * line.quantity)
                                tot_ins_approved_amt += qty_price_unit_total
                        else:
                            consultation_companies = [ins_company.id for ins_company in
                                                      line.product_id.consultation_insurance_company_ids]
                            if record.insurance_company.id == record.insurance_card.company_id.id \
                                    and record.insurance_company.id in consultation_companies:
                                is_consultation = 1
                                tot_consult_approved_amt += line.price_subtotal
                                consultation_net_amt += line.price_subtotal
                                consultation_original_amt += line.price_unit
                        patient_copayment += line.price_initial_copay
                    if not record.ins_approved_amt:
                        record.ins_approved_amt = tot_ins_approved_amt
                    if record.ins_approved_amt > tot_ins_approved_amt:
                        record.ins_approved_amt = 0.0
                    if not record.consult_approved_amt:
                        record.consult_approved_amt = tot_consult_approved_amt
                    if record.insurance_card.is_deductible:
                        check_consultation_amt = record.insurance_card.deductible
                    else:
                        check_consultation_amt = consultation_original_amt
                    if tot_consult_approved_amt < record.consult_approved_amt or record.consult_approved_amt < check_consultation_amt:
                        record.consult_approved_amt = 0.0
                    record.initial_insurance = ins_total
                    record.initial_patient_copayment = patient_copayment
                    record.consultation_net_amt = consultation_net_amt
                    amt_paid_by_patient = 0
                    if record.insurance_card.company_id.insurance_cases == 'case_1':
                        amt_paid_by_patient = record.insurance_card.company_id.amt_paid_by_patient
                    if record.insurance_card.company_id.insurance_cases in ('case_3', 'case_2'):
                        amt_paid_by_patient = record.insurance_card.amt_paid_by_patient
                    ins_copayment_total = 0.0
                    consu_copayment_total = 0.0
                    if is_treatment == 1:
                        record.is_treatment = True
                    if is_consultation == 1:
                        record.is_consultation = True
                    if record.consult_approved_amt:
                        if record.insurance_card.is_deductible:
                            consu_copayment_total = record.insurance_card.deductible
                        else:
                            consu_copayment_total = consultation_original_amt
                    if record.insurance_card.co_payment_method == 'Percentage':
                        # if record.ins_approved_amt:
                        ins_copayment_total = (record.ins_approved_amt * amt_paid_by_patient) / 100
                    if record.insurance_card.co_payment_method == 'Amount':
                        # if record.ins_approved_amt:
                        if record.ins_approved_amt < record.insurance_card.amt_fixed_paid_by_patient:
                            ins_copayment_total = record.ins_approved_amt
                        else:
                            ins_copayment_total = record.insurance_card.amt_fixed_paid_by_patient
                    patient_copayment_total = ins_copayment_total + consu_copayment_total
                    record.patient_copayment_total = patient_copayment_total
                    insurance_total_all = record.ins_approved_amt + record.consult_approved_amt - patient_copayment_total
                    if record.insurance_company.approved_amt_based_on == 'after_treatment_grp_disc':
                        record.insurance_total = insurance_total_all
                    if record.insurance_company.approved_amt_based_on == 'gross_amount':
                        record.insurance_total = insurance_total_all - record.treatment_group_disc_total
                    if record.insurance_total < 0:
                        record.ins_approved_amt = 0.0

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type', 'discount_fixed_percent', 'discount',
                 'discount_value','ins_approved_amt', 'consult_approved_amt', 'is_special_case', 'share_based_on',
                 'insurance_share', 'patient_share', 'insurance_company', 'insurance_card', 'after_treatment_grp_disc')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount_total for line in self.tax_line_ids)
        self.amount_before_disc = self.amount_untaxed + self.amount_tax
        if self.is_patient and self.patient and self.insurance_card and self.insurance_company:
            if self.is_special_case:
                total_insurance_share, total_patient_share = self.get_patient_insurance_amt()
                self_amount_total = total_patient_share
            else:
                consultation_original_amt = 0.0
                for line in self.invoice_line_ids:
                    if not line.apply_insurance:
                        consultation_companies = [ins_company.id for ins_company in
                                                  line.product_id.consultation_insurance_company_ids]
                        if self.insurance_company.id == self.insurance_card.company_id.id and \
                                        self.insurance_company.id in consultation_companies:
                            consultation_original_amt += line.price_unit
                ins_patient_total = 0.0
                cons_patient_total = 0.0
                non_cov_ins_patient_total = 0.0
                if self.consult_approved_amt:
                    if self.insurance_card.is_deductible:
                        cons_patient_total = self.insurance_card.deductible
                    else:
                        cons_patient_total = consultation_original_amt
                # if self.ins_approved_amt:
                tot_ins_approved_amt = 0.0
                for line in self.invoice_line_ids:
                    if line.apply_insurance:
                        if self.insurance_company.approved_amt_based_on == 'after_treatment_grp_disc':
                            tot_ins_approved_amt += line.price_subtotal
                        if self.insurance_company.approved_amt_based_on == 'gross_amount':
                            qty_price_unit_total = (line.price_unit * line.quantity)
                            tot_ins_approved_amt += qty_price_unit_total
                    else:
                        non_coverage_companies = [ins_company.id for ins_company in
                                                  line.product_id.non_coverage_insurance_company_ids]
                        if self.insurance_company.id == self.insurance_card.company_id.id and self.insurance_company.id in non_coverage_companies:
                            non_cov_ins_patient_total += line.price_subtotal
                difference_amt = tot_ins_approved_amt - self.ins_approved_amt
                copay = self.patient_copayment_total - cons_patient_total
                ins_patient_total = difference_amt + copay
                self_amount_total = ins_patient_total + cons_patient_total + non_cov_ins_patient_total
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


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def edit_amt_paid_by_patient(self):
        contextt = {}
        contextt['default_invoice_line'] = self.id
        return {
            'name': _('Update Co-pay'),
            'view_id': self.env.ref('detailed_insurance.view_update_copay_wizard_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'update.copay.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.one
    @api.depends('amt_paid_by_patient', 'amt_paid_by_insurance', 'discount_amt', 'invoice_id.insurance_company',
                 'price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'invoice_id.date', 'discount_fixed_percent', 'discount',
                 'discount_value', 'after_treatment_grp_disc', 'share_based_on')
    def _compute_price(self):
        treatment_companies = [ins_company.id for ins_company in self.product_id.insurance_company_ids]
        patient_companies = [insurance.company_id.id for insurance in self.partner_id.insurance_ids]
        price_subtotal_signed = self.quantity * self.price_unit
        price_initial_copay = self.quantity * self.price_unit

        if self.discount_fixed_percent == 'Percent':
            price_subtotal_signed = price_subtotal_signed * (1 - (self.discount or 0.0) / 100.0)
        if self.discount_fixed_percent == 'Fixed':
            price_subtotal_signed = price_subtotal_signed - self.discount_value

        if self.invoice_id.insurance_company.id in treatment_companies \
                and self.invoice_id.insurance_company.id in patient_companies:
            if self.insurance_cases == 'case_1':
                price_initial_copay = price_subtotal_signed * (
                    1 - (100 - self.amt_paid_by_patient or 0.0) / 100.0)
                treatment_total = (price_subtotal_signed * self.discount_amt) / 100
                total_payable = price_subtotal_signed - treatment_total
                price_subtotal_signed = total_payable
            if self.insurance_cases in ('case_3', 'case_2'):
                treatment_total = (price_subtotal_signed * self.discount_amt) / 100
                total_payable = price_subtotal_signed - treatment_total
                price_subtotal_signed = total_payable
                price_initial_copay = (total_payable * self.amt_paid_by_patient) / 100
        if self.invoice_id.is_special_case and self.invoice_id.share_based_on == 'Treatment':
            price_subtotal_signed = self.after_treatment_grp_disc
        if self.invoice_id.is_special_case and self.invoice_id.share_based_on == 'Global':
            price_subtotal_signed = 0.0
        self.price_initial_copay = price_initial_copay
        self.price_subtotal = price_subtotal_signed
        self.price_total = price_subtotal_signed
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(
                price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

    @api.onchange('amt_paid_by_patient', 'discount_amt')
    @api.depends('amt_paid_by_patient', 'discount_amt')
    def onchange_amt(self):
        for this in self:
            if this.apply_insurance:
                if this.insurance_cases == 'case_1':
                    if 100 - (this.amt_paid_by_patient + this.discount_amt) < 0:
                        raise UserError('Please enter valid amount')
                    this.amt_paid_by_insurance = 100 - (this.amt_paid_by_patient + this.discount_amt)
                if this.insurance_cases in ('case_3', 'case_2'):
                    if 100 - this.amt_paid_by_patient < 0:
                        raise UserError('Please enter valid amount')
                    this.amt_paid_by_insurance = 100 - this.amt_paid_by_patient

    @api.model
    def create(self, vals):
        if vals.get('amt_paid_by_insurance') and vals.get('amt_paid_by_patient') and vals.get('discount_amt') \
                and vals.get('apply_insurance'):
            if vals.get('insurance_cases') == 'case_1' and vals.get('amt_paid_by_insurance') + vals.get(
                    'amt_paid_by_patient') + vals.get('discount_amt') != 100:
                raise UserError('Cumulative percentage should be 100')
            if vals.get('insurance_cases') in ('case_3', 'case_2') and vals.get('amt_paid_by_insurance') and vals.get(
                    'amt_paid_by_patient') != 100:
                raise UserError('Cumulative percentage should be 100')
        return super(AccountInvoiceLine, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(AccountInvoiceLine, self).write(vals)
        if self.apply_insurance:
            if self.insurance_cases == 'case_1' and self.amt_paid_by_insurance + self.amt_paid_by_patient + \
                    self.discount_amt != 100:
                raise UserError('Cumulative percentage should be 100')
            if self.insurance_cases in (
            'case_3', 'case_2') and self.amt_paid_by_insurance + self.amt_paid_by_patient != 100:
                raise UserError('Cumulative percentage should be 100')
        return res
