# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    advance = fields.Boolean('Is Advance Payment?')
    adv_pay_amount = fields.Float(string='Invoice Amount')

    def action_validate_invoice_payment(self):
        invoice_defaults = self.invoice_ids
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            if self.amount > invoice['residual']:
                raise UserError('Payment Amt should not be greater than Due amt')
        res = super(AccountPayment, self).action_validate_invoice_payment()
        return res

    @api.multi
    def update_payment(self):
        if self.advance:
            raise UserError(_("Cant able to modify Advance payment"))
        contextt = {}
        contextt['default_payment_id'] = self.id
        contextt['default_amount'] = self.amount
        contextt['default_journal_id'] = self.journal_id.id
        return {
            'name': _('Update Payment'),
            'view_id': self.env.ref('update_invoice_payment.view_update_wizard_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'update.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def delete_payment(self):
        if self.advance:
            raise UserError(_("Cant able to delete Advance payment"))
        if any(len(record.invoice_ids) > 1 for record in self):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(_("This method should only be called to process a single invoice's payment."))
        if not self.journal_id.update_posted:
            self.journal_id.write({'update_posted': True})
        self.cancel()
        if len(self.invoice_ids) ==1:
            msg = "<b> Deleted Payment:</b><ul>"
            if self.name:
                msg += "<li>" + _("Payment") + ": %s<br/>" % (self.name)
            if self.amount:
                msg += "<li>" + _("Amount") + ": %s  <br/>" % (self.amount)
            if self.journal_id:
                msg += "<li>" + _("Journal") + ": %s  <br/>" % (self.journal_id.name)
            if self.communication:
                msg += "<li>" + _("Memo") + ": %s  <br/>" % (self.communication)
            msg += "</ul>"
            self.invoice_ids.message_post(body=msg)
        self._cr.execute('delete from update_wizard WHERE payment_id=%s', ([self.id]))
        self._cr.execute('delete from account_payment WHERE id=%s', ([self.id]))
