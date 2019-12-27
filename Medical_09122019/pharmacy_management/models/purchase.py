# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrderLIne(models.Model):
    _inherit = "purchase.order.line"

    lot_id = fields.Many2one('stock.production.lot', 'Product Lot')
    show_lot_visible = fields.Boolean('Lot Visible', compute='_compute_show_lot_visible')


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_pharmacy = fields.Boolean('Pharmacy', help="Check if the Purchase order is Pharmaceutical")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

    # .......................Automatic stock updation(lot creation from po line) while po confirmation.......................
    def get_invoice_vals_bills(self):
        invoice_vals = super(PurchaseOrder, self).get_invoice_vals_bills()
        if self.is_pharmacy:
            invoice_vals['is_pharmacy'] = True
        return invoice_vals

    # .......................New view for Smart button for bills in Purchase order.......................
    @api.multi
    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_invoice_tree2')
        # if self.is_pharmacy:
        #     action = self.env.ref('pharmacy_management.action_pharm_invoice_tree2')
        result = action.read()[0]

        # override the context to get rid of the default filtering
        result['context'] = {'type': 'in_invoice', 'default_purchase_id': self.id}

        if not self.invoice_ids:
            # Choose a default account journal in the same currency in case a new invoice is created
            journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id),
                ('currency_id', '=', self.currency_id.id),
            ]
            default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
            if default_journal_id:
                result['context']['default_journal_id'] = default_journal_id.id
            if self.is_pharmacy:
                result['context']['default_is_pharmacy'] = True
        else:
            # Use the same account journal than a previous invoice
            result['context']['default_journal_id'] = self.invoice_ids[0].journal_id.id
        # choose the view_mode accordingly
        if len(self.invoice_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        elif len(self.invoice_ids) == 1:
            res = self.env.ref('account.invoice_supplier_form', False)
            if self.is_pharmacy:
                res = self.env.ref('pharmacy_management.pharmacy_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.invoice_ids.id
        return result
