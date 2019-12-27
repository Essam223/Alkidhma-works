# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # treatment_grp_disc = fields.Float('Treatment group discount', states={'draft': [('readonly', False)]},
    #                                   track_visibility='always')
    #
    # @api.onchange('treatment_grp_disc')
    # def onchange_treatment_grp_disc(self):
    #     if self.is_patient and self.insurance_card and self.insurance_company:
    #         if self.share_based_on == 'Global':
    #             total_treatment_grp_disc = 0
    #             item_total = 0
    #             for line in self.invoice_line_ids:
    #                 item_total = (line.price_unit * line.quantity)
    #                 if line.discount_fixed_percent == 'Percent':
    #                     item_total = item_total * (1 - (line.discount or 0.0) / 100.0)
    #                 if line.discount_fixed_percent == 'Fixed':
    #                     item_total = item_total - line.discount_value
    #                 total_treatment_grp_disc += item_total
    #
    #             self.after_treatment_grp_disc = total_treatment_grp_disc - self.treatment_grp_disc

    @api.onchange('after_treatment_grp_disc')
    def onchange_after_treatment_grp_disc(self):
        if self.is_patient and self.insurance_card and self.insurance_company and not self.discount_fixed_percent:
            if self.share_based_on == 'Global':
                # self.patient_share = 0.0
                # self.insurance_share = 0.0
                if self.after_treatment_grp_disc > self.amount_subtotal:
                    self.after_treatment_grp_disc = 0.0

    @api.onchange('is_special_case')
    def onchange_is_special_case(self):
        if self.is_special_case:
            self.share_based_on = 'Treatment'
        if not self.is_special_case:
            self.share_based_on = False
            self.insurance_share = 0.0
            self.patient_share = 0.0
            self.after_treatment_grp_disc = 0.0
            for line in self.invoice_line_ids:
                line.insurance_share = 0.0
                line.patient_share = 0.0
                line.after_treatment_grp_disc = 0.0

    @api.onchange('share_based_on')
    def onchange_share_based_on(self):
        if self.share_based_on == 'Global':
            insurance_share = 0.0
            patient_share = 0.0
            treatment_grp_disc = 0.0
            inv_after_treatment_grp_disc = 0.0
            for line in self.invoice_line_ids:
                patient_share += line.price_initial_copay
                item_total = (line.price_unit * line.quantity)
                if line.discount_fixed_percent == 'Percent':
                    item_total = item_total * (1 - (line.discount or 0.0) / 100.0)
                if line.discount_fixed_percent == 'Fixed':
                    item_total = item_total - line.discount_value
                treatment_grp_disc = (item_total * line.discount_amt) / 100
                after_treatment_grp_disc = item_total - ((item_total * line.discount_amt) / 100)
                insurance_share += after_treatment_grp_disc - line.price_initial_copay
                inv_after_treatment_grp_disc += after_treatment_grp_disc
            self.insurance_share = insurance_share
            self.patient_share = patient_share
            self.after_treatment_grp_disc = inv_after_treatment_grp_disc
            self.treatment_grp_disc = treatment_grp_disc

        for line in self.invoice_line_ids:
            line.insurance_share = 0.0
            line.patient_share = 0.0
            line.after_treatment_grp_disc = 0.0
            line.price_subtotal = 0.0
            line.price_total = 0.0
            if self.share_based_on == 'Treatment':
                line.patient_share = line.price_initial_copay
                item_total = (line.price_unit * line.quantity)
                if line.discount_fixed_percent == 'Percent':
                    item_total = item_total * (1 - (line.discount or 0.0) / 100.0)
                if line.discount_fixed_percent == 'Fixed':
                    item_total = item_total - line.discount_value
                after_treatment_grp_disc = item_total - ((item_total * line.discount_amt) / 100)
                line.after_treatment_grp_disc = after_treatment_grp_disc
                line.insurance_share = after_treatment_grp_disc - line.price_initial_copay


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"


