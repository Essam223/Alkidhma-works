from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class CompletedReversal(models.TransientModel):
    _name = 'completed.reversal'

    reason_reversal = fields.Text('Reason for Reversal', required=True)
    warning_msg = fields.Text('Warning')
    appt_id = fields.Many2one('medical.appointment', 'Appointment', required=True)

    def do_invoice_cancel(self, appt_invoice_id, appt):
        if appt_invoice_id.type == 'out_refund':
            msg = "<b> Cancelled Credit Note:</b><ul>"
        else:
            msg = "<b> Cancelled Invoice:</b><ul>"
        if appt_invoice_id.number:
            msg += "<li>" + _("Number") + ": %s  <br/>" % (appt_invoice_id.number)
        if appt_invoice_id.state == 'draft':
            appt_invoice_id.write({'move_name': False})
        if appt_invoice_id.state == 'open' and not appt_invoice_id.payment_ids:
            appt_invoice_id.modify_invoice()
        if appt_invoice_id.state == 'open' and appt_invoice_id.payment_ids:
            for paymt in appt_invoice_id.payment_ids:
                paymt.cancel()
            appt_invoice_id.modify_invoice()
        if appt_invoice_id.state == 'cancel':
            appt_invoice_id.action_invoice_draft()
        if appt_invoice_id.state == 'paid':
            for paymt in appt_invoice_id.payment_ids:
                paymt.cancel()
            appt_invoice_id.modify_invoice()
        appt_invoice_id.write({'state': 'draft', 'move_name': False})
        if appt_invoice_id.amount_total_signed:
            msg += "<li>" + _("Amount") + ": %s  <br/>" % (appt_invoice_id.amount_total_signed)
        msg += "</ul>"
        appt.message_post(body=msg)
        for paymt in appt_invoice_id.payment_ids:
            paymt.cancel()
        appt_invoice_id.action_invoice_cancel()

    @api.multi
    def action_confirm(self):
        wizard_vals = self.read()[0]
        if wizard_vals['appt_id']:
            appt = self.env['medical.appointment'].browse(wizard_vals['appt_id'][0])
            if appt.invoice_id:
                if appt.invoice_id.number:
                    credit_note = self.env['account.invoice'].search([('origin', '=', appt.invoice_id.number)])
                    for c_note in credit_note:
                        self.do_invoice_cancel(c_note, appt)
                self.do_invoice_cancel(appt.invoice_id, appt)
            appt.write({'reason_reversal': wizard_vals['reason_reversal'],
                        'state': 'ready', 'invoice_id':False})