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
            if self.insurance_id:
                for inv_line in inv_id.invoice_line_ids:
                    if self.insurance_id.company_id.id in [comp.id for comp in
                                                           inv_line.product_id.insurance_company_ids]:
                        inv_line.write({'insurance_cases': self.insurance_id.company_id.insurance_cases})
                inv_id.write({'share_based_on': 'Global'})
                inv_id.onchange_insurance_company()
                inv_id._get_ins_company_domain()
        return res
