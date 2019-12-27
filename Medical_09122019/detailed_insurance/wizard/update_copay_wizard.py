from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class UpdateCopayWizard(models.TransientModel):
    _name = 'update.copay.wizard'

    amount_copay = fields.Float('Co-payment')
    invoice_line = fields.Many2one('account.invoice.line', 'Invoice line', required=True)

    @api.multi
    def action_confirm(self):
        wizard_vals = self.read()[0]
        if wizard_vals['invoice_line']:
            invoice_line = self.env['account.invoice.line'].browse(wizard_vals['invoice_line'][0])
            if invoice_line.invoice_id.insurance_card and invoice_line.invoice_id.is_patient \
                    and invoice_line.invoice_id.is_special_case:
                if invoice_line.invoice_id.insurance_card.co_payment_method == 'Percentage':
                    if wizard_vals['amount_copay'] > 100:
                        raise UserError(_('Discount Percentage should not be greater than 100'))
                    invoice_line.write({'amt_paid_by_patient': wizard_vals['amount_copay']})
                if invoice_line.invoice_id.insurance_card.co_payment_method == 'Amount':
                    invoice_line.write({'amt_fixed_paid_by_patient': wizard_vals['amount_copay']})