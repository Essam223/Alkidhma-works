# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    payment_ids = fields.One2many('account.payment', compute="_compute_payment_ids", string='Payments')
    credit_amt = fields.Float('Card Amount', digits=dp.get_precision('Product Price'), compute='_compute_credit_cash_amt')
    cash_amt = fields.Float('Cash Amount', digits=dp.get_precision('Product Price'), compute='_compute_credit_cash_amt')

    def _compute_credit_cash_amt(self):
        for invoice in self:
            cash_amt = 0.0
            credit_amt = 0.0
            for statement in invoice.payment_ids:

                if statement.state in ('posted', 'reconciled'):
                    for inv in statement.invoice_ids:
                        if inv.id == invoice.id:
                            payments_vals = invoice._get_payments_vals()
                            for paymt in payments_vals:
                                payment_id = paymt['account_payment_id']
                                amount = paymt['amount']
                                if payment_id == statement.id:
                                    if statement.journal_id.type == 'cash':
                                        cash_amt += amount
                                    if statement.journal_id.type == 'bank':
                                        credit_amt += amount
            invoice.credit_amt = credit_amt
            invoice.cash_amt = cash_amt

    @api.one
    def _compute_payment_ids(self):
        payments_vals = self._get_payments_vals()
        for paymt in  payments_vals:
            payment_id = paymt['account_payment_id']
            amount = paymt['amount']
            self.env['account.payment'].browse(payment_id).write({'adv_pay_amount': amount})
        self.payment_ids = self.env["account.payment"].search([("invoice_ids", "=", self.id)])

    adv_amount = fields.Float(string='Adv Dummy Amount', compute='get_adv_pay_amount')

    @api.one
    def get_adv_pay_amount(self):
        self._compute_payment_ids()
        self.adv_amount = 1

    @api.multi
    def add_discount(self):
        contextt = {}
        contextt['default_invoice_id'] = self.id
        # contextt['default_discount_after_validation'] = self.residual
        return {
            'name': _('Add discount'),
            'view_id': self.env.ref('update_invoice_payment.view_add_discount_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'add.discount',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def modify_invoice(self):
        moves = self.env['account.move']
        for inv in self:
            if inv.move_id:
                moves += inv.move_id
            if inv.payment_move_line_ids:
                raise UserError(_('You cannot cancel an invoice which is partially paid. You need to unreconcile related payment entries first.'))
        self.write({'state': 'draft', 'date': False, 'move_id': False})
        if not self.journal_id.update_posted:
            self.journal_id.write({'update_posted': True})
        if moves:
            moves.button_cancel()
            moves.unlink()
        try:
            report_invoice = self.env['ir.actions.report']._get_report_from_name('account.report_invoice')
        except IndexError:
            report_invoice = False
        if report_invoice and report_invoice.attachment:
            for invoice in self:
                with invoice.env.do_in_draft():
                    invoice.number, invoice.state = invoice.move_name, 'open'
                    attachment = self.env.ref('account.account_invoices').retrieve_attachment(invoice)
                if attachment:
                    attachment.unlink()