from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class UpdateWizard(models.TransientModel):
    _inherit = 'update.wizard'

    @api.multi
    def action_confirm(self):
        res = super(UpdateWizard, self).action_confirm()
        wizard_vals = self.read()[0]
        if wizard_vals['payment_id']:
            payment = self.env['account.payment'].browse(wizard_vals['payment_id'][0])
            if len(payment.payslip_ids) == 1:
                if payment.payslip_ids.residual:
                    payment.payslip_ids.write({'state': 'confirmed'})
                else:
                    payment.payslip_ids.write({'state': 'done'})
        return res