# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Partner(models.Model):
    _inherit = "res.partner"

    approved_amt_based_on = fields.Selection([('gross_amount', 'Gross amount'),
                                              ('after_treatment_grp_disc', 'After Treatment group disc')],
                                             'Approved amount based on', track_visibility='always',
                                             default='after_treatment_grp_disc', required=True)

    @api.onchange('amt_paid_by_patient', 'discount_amt', 'insurance_cases')
    @api.depends('amt_paid_by_patient', 'amt_paid_by_insurance', 'discount_amt', 'insurance_cases')
    def onchange_amt(self):
        if self.insurance_cases == 'case_1':
            if 100 - (self.amt_paid_by_patient + self.discount_amt) < 0:
                raise UserError('Please enter valid amount')
            self.amt_paid_by_insurance = 100 - (self.amt_paid_by_patient + self.discount_amt)
        if self.insurance_cases in ('case_3', 'case_2'):
            self.amt_paid_by_patient = 0.0
            self.amt_paid_by_insurance = 0.0

    @api.model
    def create(self, vals):
        if vals.get('is_insurance_company') == True:
            if vals.get('insurance_cases') == 'case_1' and vals.get('amt_paid_by_insurance') + \
                    vals.get('amt_paid_by_patient') + vals.get('discount_amt') != 100:
                raise UserError('Cumulative percentage should be 100')
        return super(Partner, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(Partner, self).write(vals)
        if self.is_insurance_company:
            if self.insurance_cases == 'case_1' and self.amt_paid_by_insurance + \
                    self.amt_paid_by_patient + self.discount_amt != 100:
                raise UserError('Cumulative percentage should be 100')
        return res