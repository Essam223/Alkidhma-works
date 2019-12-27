from odoo import api, fields, models


class SaleReopen(models.TransientModel):
    _name = 'sale.reopen'

    reason_reversal = fields.Text('Reason for Reversal', required=True)

    @api.multi
    def action_confirm(self):
        act_id = self.env.context.get('active_ids', [])
        so = self.env['sale.order'].search([('id', 'in', act_id)])
        so.action_cancel()
        so.write({'state': 'draft', 'reason_reversal': self.reason_reversal})
        msg = "Order Reopened"
        so.message_post(body=msg)
