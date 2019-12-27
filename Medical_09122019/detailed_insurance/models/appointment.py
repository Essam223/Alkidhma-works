# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _


class MedicalAppointment(models.Model):
    _inherit = "medical.appointment"

    @api.multi
    def done(self):
        res = super(MedicalAppointment, self).done()
        if self.invoice_id:
            inv_id = self.invoice_id
            inv_id.write({'share_based_on': ''})
            if self.insurance_id:
                tot_ins_approved_amt = 0.0
                tot_consult_approved_amt = 0.0
                for inv_line in inv_id.invoice_line_ids:
                    if inv_line.apply_insurance:
                        if inv_id.insurance_company.approved_amt_based_on == 'after_treatment_grp_disc':
                            tot_ins_approved_amt += inv_line.price_subtotal
                        if inv_id.insurance_company.approved_amt_based_on == 'gross_amount':
                            qty_price_unit_total = (inv_line.price_unit * inv_line.quantity)
                            tot_ins_approved_amt += qty_price_unit_total
                    else:
                        consultation_companies = [ins_company.id for ins_company in
                                                  inv_line.product_id.consultation_insurance_company_ids]
                        if inv_id.insurance_company.id == inv_id.insurance_card.company_id.id and \
                                        inv_id.insurance_company.id in consultation_companies:
                            tot_consult_approved_amt += inv_line.price_subtotal
                inv_id.write({'ins_approved_amt': tot_ins_approved_amt,
                              'consult_approved_amt': tot_consult_approved_amt})
        return res
