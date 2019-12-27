# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    # @api.constrains('property_account_receivable_id', 'company_id', 'property_account_payable_id')
    # def _check_same_company_partner(self):
    #     if self.company_id:
    #         if self.property_account_receivable_id.company_id:
    #             if self.company_id.id != self.property_account_receivable_id.company_id.id:
    #                 raise ValidationError(_('Error ! Partner and Account Receivable should be of same company'))
    #         if self.property_account_payable_id.company_id:
    #             if self.company_id.id != self.property_account_payable_id.company_id.id:
    #                 raise ValidationError(_('Error ! Partner and Account Payable should be of same company'))

    date = fields.Date('Partner since', help="Date of activation of the partner or patient")
    alias = fields.Char('alias', size=64)
    is_patient = fields.Boolean('Patient', help="Check if the partner is a patient")
    is_doctor = fields.Boolean('Doctor', help="Check if the partner is a doctor")
    is_insurance_company = fields.Boolean('Insurance Company', help="Check if the partner is a Insurance Company")
    middle_name = fields.Char('Middle Name', size=128, help="Middle Name")
    lastname = fields.Char('Last Name', size=128, help="Last Name")
    insurance_ids = fields.One2many('medical.insurance', 'name', "Insurance")
    treatment_ids = fields.Many2many('product.product', 'treatment_insurance_company_relation', 'treatment_id',
                                     'insurance_company_id', 'Coverage Treatments')
    non_coverage_treatment_ids = fields.Many2many('product.product', 'non_coverage_treatment_insurance_company_relation'
                                                  , 'non_coverage_treatment_id', 'non_coverage_insurance_company_id',
                                                  'Non-Coverage Treatments')
    consultation_treatment_ids = fields.Many2many('product.product', 'consultation_treatment_insurance_company_relation'
                                                  , 'consultation_treatment_id', 'consultation_insurance_company_id',
                                                  'Consultation charges')
    amt_paid_by_patient = fields.Float('Co-payment(%)')
    amt_paid_by_insurance = fields.Float('Amount by Insurance(%)')
    discount_amt = fields.Float('Treatment Group Discount(%)')
    nationality_id = fields.Char('Qatar Nationality ID')
    registration_fee_amount = fields.Float('Registration fee')
    state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid')], 'State', default='draft')
    registration_inv_id = fields.Many2one('account.invoice', 'Registration Invoice')
    registration_invoice = fields.Boolean('Registration Invoice ?', _defult=0)
    patient_id = fields.Char('Patient ID', size=64,
                             help="Patient Identifier provided by the Health Center.", compute='compute_patient_id')
    insurance_cases = fields.Selection([('case_1', 'Case 1'),('case_2', 'Case 2'), ('case_3', 'Case 3')], 'Insurance Type', default='case_1')
    insur_report_format = fields.Selection([('nextcare_allianz', 'Nextcare and Allianz'), ('qlm', 'QLM')],
                                           'Report Format')
    is_deductible = fields.Boolean('Is Deductible?')

    @api.depends('is_patient')
    def compute_patient_id(self):
        for record in self:
            record.patient_id = False
            patient_exist = self.env['medical.patient'].search([('name', '=', record.id)])
            if patient_exist:
                record.patient_id = patient_exist[0].patient_id

    @api.multi
    @api.depends('name', 'last_name', 'middle_name', 'patient_id', 'company_id')
    def name_get(self):
        result = []
        for partner in self:
            name = partner.name
            patient_exist = self.env['medical.patient'].search([('name', '=', partner.id)])
            if partner.is_patient and patient_exist:
                    partner_patient = patient_exist[0]
                    if partner_patient.patient_id:
                        name = '[' + partner_patient.patient_id + ']' + name
                    # if partner_patient.mobile:
                    #     name = name + " : " + partner_patient.mobile
            else:
                name = partner.name or ''
                if partner.middle_name:
                    name += ' ' + partner.middle_name
                if partner.lastname:
                    name = partner.lastname + ', ' + name
            if partner.is_insurance_company:
                if self.env.user.has_group('base.group_multi_company'):
                    name = partner.company_id.name + ' - ' + name
            result.append((partner.id, name))
        return result

    @api.multi
    def get_user_name(self):
        return self.name
