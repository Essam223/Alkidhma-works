# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrderLIne(models.Model):
    _inherit = "purchase.order.line"

    lot_id = fields.Many2one('stock.production.lot', 'Product Lot')
    show_lot_visible = fields.Boolean('Lot Visible', compute='_compute_show_lot_visible')

    @api.depends('product_id')
    def _compute_show_lot_visible(self):
        for po_line in self:
            if not po_line.product_id:
                po_line.show_lot_visible = False
                continue
            if po_line.product_id.tracking == 'lot':
                po_line.show_lot_visible = True
            else:
                po_line.show_lot_visible = False

    @api.onchange('product_id')
    def onchange_product_id(self):
        domain = super(PurchaseOrderLIne, self).onchange_product_id()
        self.lot_id = False
        return domain


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

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
        journal_domain = [
            ('type', '=', 'purchase'),
            ('company_id', '=', self.company_id.id),
        ]
        default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
        invoice_vals = {
            'type': 'in_invoice',
            'journal_type': 'purchase',
            'user_id': self.env.user.id,
            'account_id': self.partner_id.property_account_payable_id.id,
            'purchase_id': self.id,
            'origin': self.name,
            'partner_id': self.partner_id.id,
            'journal_id': default_journal_id.id,
        }
        return invoice_vals

    @api.multi
    def button_confirm(self):
        for ol in self.order_line:
            if ol.show_lot_visible and not ol.lot_id:
                raise UserError(_("No Lot defined for the Product %s, please configure one.") % (ol.product_id.name))
        result = super(PurchaseOrder, self).button_confirm()
        for picking in self.picking_ids:
            if picking.state not in ('done', 'cancel'):
                picking.action_confirm()
                picking.action_assign()
                wrong_lots = self.set_po_pack_operation_lot(picking)
                # if picking.state != 'done':
                #     no_quantities_done = all(line.qty_done == 0.0 for line in picking.move_line_ids)
                #     no_initial_demand = all(move.product_uom_qty == 0.0 for move in picking.move_lines)
                #     if not(no_initial_demand and no_quantities_done):
                #         picking.button_validate()
                if not wrong_lots:
                    picking.action_done()
        invoice_vals = self.get_invoice_vals_bills()
        v_bill = self.env['account.invoice'].create(invoice_vals)
        v_bill.purchase_order_change()
        return result

    def set_po_pack_operation_lot(self, picking):
        """Set Serial/Lot number in pack operations to mark the pack operation done."""
        StockProductionLot = self.env['stock.production.lot']
        PurchOrderLine = self.env['purchase.order.line']
        has_wrong_lots = False
        for del_move in picking.move_lines:
            del_move.move_line_ids.unlink()
        for move in picking.move_lines:
            picking_type = picking.picking_type_id
            # lots_necessary = True
            if picking_type:
                if not picking_type.use_existing_lots:
                    picking_type.write({'use_existing_lots': True})
                    # lots_necessary = picking_type and picking_type.use_existing_lots
            qty = 0
            qty_done = 0
            pack_lots = []
            pack_lot_id = []
            for ord_line in self.order_line:
                if ord_line.lot_id and ord_line.lot_id.product_id.id == move.product_id.id:
                    pack_lot_id.append(ord_line.lot_id.id)
            # if pack_lot_names and lots_necessary:
            if pack_lot_id:
                for lot_id in list(set(pack_lot_id)):
                    stock_production_lot = StockProductionLot.search(
                        [('id', '=', lot_id), ('product_id', '=', move.product_id.id)])
                    if len(self.order_line) == len(picking.move_lines):
                        p_order_line = PurchOrderLine.search([('lot_id', '=', lot_id), ('order_id', '=', self.id),
                                                              ('product_id', '=', move.product_id.id),
                                                              ('id', '=', move.purchase_line_id.id)])
                    else:
                        p_order_line = PurchOrderLine.search([('lot_id', '=', lot_id), ('order_id', '=', self.id),
                                                              ('product_id', '=', move.product_id.id)])
                    if stock_production_lot and p_order_line:
                        if stock_production_lot.product_id.tracking == 'lot':
                            # if a lot nr is set through the frontend it will refer to the full quantity
                            qty = p_order_line[0].product_qty
                        else:  # serial numbers
                            qty = 1.0
                        qty_done += qty
                        pack_lots.append({'lot_id': stock_production_lot.id, 'qty': qty})
                    else:
                        has_wrong_lots = True
            # elif move.product_id.tracking == 'none' or not lots_necessary:
            elif move.product_id.tracking == 'none':
                qty_done = move.product_uom_qty
            else:
                has_wrong_lots = True
            for pack_lot in pack_lots:
                lot_id, qty = pack_lot['lot_id'], pack_lot['qty']
                self.env['stock.move.line'].create({
                    'move_id': move.id,
                    'product_id': move.product_id.id,
                    'product_uom_id': move.product_uom.id,
                    'qty_done': qty,
                    'location_id': move.location_id.id,
                    'location_dest_id': move.location_dest_id.id,
                    'lot_id': lot_id,
                })
                move.write({'qty_done': qty})
            if not pack_lots:
                move.quantity_done = qty_done
        return has_wrong_lots

    # .......................Purchase cancellation - Bill and delivery cancellation.......................
    def _prepare_move_default_values(self, res, return_line_move_id, return_line_quantity, return_line_product_id,
                                     new_picking):
        vals = {
            'product_id': return_line_product_id.id,
            'product_uom_qty': return_line_quantity,
            'picking_id': new_picking.id,
            'state': 'draft',
            'purchase_line_id': return_line_move_id.purchase_line_id.id,
            'location_id': return_line_move_id.location_dest_id.id,
            'location_dest_id': res['location_id'].id or return_line_move_id.location_id.id,
            'picking_type_id': new_picking.picking_type_id.id,
            'warehouse_id': res['picking_id'].picking_type_id.warehouse_id.id,
            'origin_returned_move_id': return_line_move_id.id,
            'procure_method': 'make_to_stock',
        }
        return vals

    def _create_returns(self, res):
        product_return_moves = res['product_return_moves']
        picking_id = res['picking_id']
        location_id = res['location_id']
        for p_return_moves in product_return_moves:
            return_move = self.env['stock.move'].browse(p_return_moves[2]['move_id'])
            return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()
        # create new picking for returned products
        picking_type_id = picking_id.picking_type_id.return_picking_type_id.id or picking_id.picking_type_id.id
        new_picking = picking_id.copy({
            'move_lines': [],
            'picking_type_id': picking_type_id,
            'state': 'draft',
            'origin': _("Return of %s") % picking_id.name,
            'location_id': picking_id.location_dest_id.id,
            'location_dest_id': location_id.id})
        new_picking.message_post_with_view('mail.message_origin_link',
                                           values={'self': new_picking, 'origin': picking_id},
                                           subtype_id=self.env.ref('mail.mt_note').id)
        returned_lines = 0
        for p_return_moves in product_return_moves:
            return_line_move_id = self.env['stock.move'].browse(p_return_moves[2]['move_id'])
            return_line_quantity = p_return_moves[2]['quantity']
            return_line_product_id = self.env['stock.move'].browse(p_return_moves[2]['move_id']).product_id
            if not return_line_move_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed"))
            if return_line_quantity:
                returned_lines += 1
                vals = self._prepare_move_default_values(res, return_line_move_id, return_line_quantity,
                                                         return_line_product_id, new_picking)
                r = return_line_move_id.copy(vals)
                vals = {}
                move_orig_to_link = return_line_move_id.move_dest_ids.mapped('returned_move_ids')
                move_dest_to_link = return_line_move_id.move_orig_ids.mapped('returned_move_ids')
                vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link | return_line_move_id]
                vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                r.write(vals)
        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))
        new_picking.action_confirm()
        new_picking.action_assign()
        wrong_lots = self.set_po_pack_operation_lot(new_picking)
        if not wrong_lots:
            new_picking.action_done()
        # if new_picking.state != 'done':
        #     new_picking.button_validate()
        # wizard = self.env[(res_dict.get('res_model'))].browse(res_dict.get('res_id'))
        # wizard.process()
        return new_picking, picking_type_id

    def create_returns(self, res):
        for wizard in self:
            new_picking_id, pick_type_id = wizard._create_returns(res)
            return new_picking_id

    def po_stock_delivery_cancel(self, picking):
        if picking:
            if picking.state != 'done':
                picking.action_cancel()
            else:
                res = {}
                move_dest_exists = False
                product_return_moves = []
                res.update({'picking_id': picking})
                # move_list =
                for move in picking.move_lines:
                    if move.scrapped:
                        continue
                    if move.move_dest_ids:
                        move_dest_exists = True
                    quantity = move.product_qty - sum(move.move_dest_ids.filtered(
                        lambda m: m.state in ['partially_available', 'assigned', 'done']). \
                                                      mapped('move_line_ids').mapped('product_qty'))
                    product_return_moves.append(
                        (0, 0, {'product_id': move.product_id.id, 'quantity': quantity, 'move_id': move.id}))
                if not product_return_moves:
                    raise UserError(_(
                        "No products to return (only lines in Done state and not fully returned yet can be returned)!"))
                res.update({'product_return_moves': product_return_moves})
                res.update({'move_dest_exists': move_dest_exists})
                if picking.location_id.usage == 'internal':
                    res.update({
                        'parent_location_id': picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.view_location_id.id or picking.location_id.location_id.id})
                res.update({'original_location_id': picking.location_id.id})
                location_id = picking.location_id
                if picking.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
                    location_id = picking.picking_type_id.return_picking_type_id.default_location_dest_id
                res['location_id'] = location_id
                self.create_returns(res)

    def po_v_bill_cancel(self, po_bill_id):
        if po_bill_id.state == 'draft':
            po_bill_id.write({'move_name': False})
        if po_bill_id.state == 'open' and not po_bill_id.payment_ids:
            po_bill_id.modify_invoice()
        if po_bill_id.state == 'open' and po_bill_id.payment_ids:
            for paymt in po_bill_id.payment_ids:
                # paymt.delete_payment()
                paymt.cancel()
            po_bill_id.modify_invoice()
        if po_bill_id.state == 'cancel':
            po_bill_id.action_invoice_draft()
        if po_bill_id.state == 'paid':
            for paymt in po_bill_id.payment_ids:
                paymt.cancel()
                # paymt.delete_payment()
            po_bill_id.modify_invoice()
        po_bill_id.write({'state': 'draft', 'move_name': False})
        po_bill_id.action_invoice_cancel()

    @api.multi
    def button_cancel(self):
        # ........Bill cancellation.........
        for inv in self.invoice_ids:
            self.po_v_bill_cancel(inv)
        # ........Stock cancellation/return.........
        for deliv in self.picking_ids:
            self.po_stock_delivery_cancel(deliv)
        self.write({'state': 'cancel'})
