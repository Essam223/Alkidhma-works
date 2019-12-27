# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ProductProduct(models.Model):
    _inherit = "product.product"

    action_perform = fields.Selection([('action', 'Action'), ('missing', 'Missing'), ('composite', 'Composite')],
                                      'Action perform', default='action')
    is_medicament = fields.Boolean('Medicament', help="Check if the product is a medicament")
    is_treatment = fields.Boolean('Treatment', help="Check if the product is a Treatment")
    is_clinic_treatment = fields.Boolean('Clinic Treatment', help="Check if the product is a Non-insurance Treatment")
    is_planned_visit = fields.Boolean('Planned Visit')
    duration = fields.Selection(
        [('three_months', 'Three Months'), ('six_months', 'Six Months'), ('one_year', 'One Year')], 'Duration')

    insurance_company_ids = fields.Many2many('res.partner', 'treatment_insurance_company_relation',
                                             'insurance_company_id', 'treatment_id', 'Insurance Company under Coverage')
    non_coverage_insurance_company_ids = fields.Many2many('res.partner', 'non_coverage_treatment_insurance_company_relation',
                                             'non_coverage_insurance_company_id', 'non_coverage_treatment_id',
                                             'Insurance Company under Non-Coverage')
    consultation_insurance_company_ids = fields.Many2many('res.partner',
                                                          'consultation_treatment_insurance_company_relation',
                                                          'consultation_insurance_company_id',
                                                          'consultation_treatment_id',
                                                          'Insurance Company under Consultation')
    discount_amt = fields.Float('Treatment Group Discount(%)')

    highlight_color = fields.Char('Highlight Color', default="ff000c")

    @api.multi
    def get_treatment_charge(self):
        return self.lst_price
