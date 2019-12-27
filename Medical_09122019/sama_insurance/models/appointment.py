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
                inv_id.write({'is_special_case': True, 'share_based_on': 'Treatment'})
                inv_id.onchange_is_special_case()
                inv_id.onchange_share_based_on()
        return res
