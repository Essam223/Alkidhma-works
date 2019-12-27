# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from datetime import date


class sale_line_obj(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.onchange('product_id')
    def check_product_kk(self):
        self.set_access_to_edit_discount()

    def set_access_to_edit_discount(self):
        for rec in self:
            if self.env.user.has_group('sale.group_discount_per_so_line'):
                rec.access_to_edit_discount = True

    access_to_edit_discount = fields.Boolean(compute=set_access_to_edit_discount, string='Edit Invoice line Discount?')
    discount_fixed_percent = fields.Selection([('Fixed', 'Fixed'), ('Percent', 'Percent')],
                                              string='Disc Fixed/Percent', default=False)
    discount = fields.Float(string='Disc (%)', digits=dp.get_precision('Discount'), default=0.0)
    discount_value = fields.Float(string='Disc Amt')

    @api.onchange('discount', 'discount_value')
    def _onchange_discount_value(self):
        if self.discount_fixed_percent == 'Fixed':
            if self.discount_value > self.price_unit:
                raise UserError(_('Discount Amount should not be greater than Total Amount.'))
        if self.discount_fixed_percent == 'Percent':
            if self.discount > 100:
                raise UserError(_('Discount Percentage should not be greater than 100'))

    @api.onchange('discount_fixed_percent')
    def _onchange_discount_fixed_percent(self):
        if not self.discount_fixed_percent:
            self.discount = ""
            self.discount_value = ""
        if self.discount_fixed_percent == 'Fixed':
            self.discount = ""
        if self.discount_fixed_percent == 'Percent':
            self.discount_value = ""

    @api.depends('product_uom_qty', 'price_unit', 'tax_id', 'discount_fixed_percent', 'discount', 'discount_value')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            self_price_subtotal = taxes['total_excluded']
            if not line.discount_fixed_percent:
                self_price_subtotal = self_price_subtotal
            if line.discount_fixed_percent == 'Percent':
                self_price_subtotal = self_price_subtotal * (1 - (line.discount or 0.0) / 100.0)
            if line.discount_fixed_percent == 'Fixed':
                self_price_subtotal = self_price_subtotal - line.discount_value
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': self_price_subtotal,
            })

    @api.depends('price_unit', 'discount')
    def _get_price_reduce(self):
        for line in self:
            price_reduce = 0.0
            if not line.discount_fixed_percent:
                price_reduce = line.price_unit
            if line.discount_fixed_percent == 'Percent':
                price_reduce = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if line.discount_fixed_percent == 'Fixed':
                price_reduce = line.price_unit - line.discount_value
            line.price_reduce = price_reduce

    @api.multi
    def _get_tax_amount_by_group(self):
        self.ensure_one()
        res = {}
        for line in self.order_line:
            base_tax = 0
            for tax in line.tax_id:
                group = tax.tax_group_id
                res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                # FORWARD-PORT UP TO SAAS-17
                price_reduce = 0.0
                if not line.discount_fixed_percent:
                    price_reduce = line.price_unit
                if line.discount_fixed_percent == 'Percent':
                    price_reduce = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                if line.discount_fixed_percent == 'Fixed':
                    price_reduce = line.price_unit - line.discount_value
                price_reduce = price_reduce
                taxes = tax.compute_all(price_reduce + base_tax, quantity=line.product_uom_qty,
                                        product=line.product_id, partner=self.partner_shipping_id)['taxes']
                for t in taxes:
                    res[group]['amount'] += t['amount']
                    res[group]['base'] += t['base']
                if tax.include_base_amount:
                    base_tax += tax.compute_all(price_reduce + base_tax, quantity=1, product=line.product_id,
                                                partner=self.partner_shipping_id)['taxes'][0]['amount']
        res = sorted(res.items(), key=lambda l: l[0].sequence)
        res = [(l[0].name, l[1]['amount'], l[1]['base'], len(res)) for l in res]
        return res

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(sale_line_obj, self)._prepare_invoice_line(qty)
        res.update({
                'discount_fixed_percent': self.discount_fixed_percent,
                'discount': self.discount,
                'discount_value': self.discount_value,
                 })
        return res

    @api.onchange('barcode')
    def _onchange_barcode(self):
        product = ""
        if self.barcode:
            if self.env['product.product'].search([('barcode', '=', self.barcode)]):
                product = self.env['product.product'].search([('barcode', '=', self.barcode)])[0]
        if product:
            self.product_id = product

    barcode = fields.Char('Barcode', help="Barcode")
    lot_id = fields.Many2one('stock.production.lot', 'Product Lot')
    show_lot_visible = fields.Boolean('Lot Visible', compute='_compute_show_lot_visible')

    @api.depends('product_id')
    def _compute_show_lot_visible(self):
        for so_line in self:
            if not so_line.product_id:
                so_line.show_lot_visible = False
                continue
            if so_line.product_id.tracking == 'lot':
                so_line.show_lot_visible = True
            else:
                so_line.show_lot_visible = False

    @api.onchange('product_id')
    def product_id_change(self):
        domain = super(sale_line_obj, self).product_id_change()
        self.lot_id = False
        return domain


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    @api.onchange('partner_id')
    def check_partner_kk(self):
        self.set_access_to_edit_discount()

    def set_access_to_edit_discount(self):
        for rec in self:
            if self.env.user.has_group('sale.group_discount_per_so_line') and rec.state == 'draft':
                rec.access_to_edit_discount = True

    access_to_edit_discount = fields.Boolean(compute=set_access_to_edit_discount, string='Edit Invoice Discount?')
    discount_fixed_percent = fields.Selection([('Fixed', 'Fixed'), ('Percent', 'Percent')],
                                              string='Disc Fixed/Percent', default=False, track_visibility='always',
                                              readonly=True, states={'draft': [('readonly', False)]})
    discount = fields.Float(string='Disc (%)', digits=dp.get_precision('Discount'), default=0.0,
                            track_visibility='always', readonly=True, states={'draft': [('readonly', False)]})
    discount_value = fields.Float(string='Disc Amt', track_visibility='always', readonly=True,
                                  states={'draft': [('readonly', False)]})

    @api.onchange('discount', 'discount_value')
    def _onchange_discount_value(self):
        if self.discount_fixed_percent == 'Fixed':
            if self.discount_value > self.amount_untaxed + self.amount_tax:
                raise UserError(_('Discount Amount should not be greater than Total Amount.'))
        if self.discount_fixed_percent == 'Percent':
            if self.discount > 100:
                raise UserError(_('Discount Percentage should not be greater than 100'))

    @api.onchange('discount_fixed_percent')
    def _onchange_discount_fixed_percent(self):
        if not self.discount_fixed_percent:
            self.discount = ""
            self.discount_value = ""
        if self.discount_fixed_percent == 'Fixed':
            self.discount = ""
        if self.discount_fixed_percent == 'Percent':
            self.discount_value = ""

    @api.depends('order_line.price_total', 'discount_fixed_percent', 'discount', 'discount_value')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            order_amount_total = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            self_amount_total = amount_untaxed + amount_tax
            if not order.discount_fixed_percent:
                order_amount_total = self_amount_total
            if order.discount_fixed_percent == 'Percent':
                order_amount_total = self_amount_total * (1 - (order.discount or 0.0) / 100.0)
            if order.discount_fixed_percent == 'Fixed':
                order_amount_total = self_amount_total - order.discount_value
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_before_disc': amount_untaxed + amount_tax,
                'amount_total': order_amount_total,
            })

    amount_before_disc = fields.Monetary(string='Before Disc', store=True, readonly=True, compute='_amount_all',
                                         track_visibility='always')

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({
            'discount_fixed_percent': self.discount_fixed_percent,
            'discount': self.discount,
            'discount_value': self.discount_value,
        })
        return res

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    is_pharmacy = fields.Boolean('Pharmacy', help="Check if the sale order is Pharmaceutical")
    reason_reversal = fields.Text('Reason for Reopen', track_visibility='onchange')

    # .......................Automatic stock updation(lot creation from so line) and inv creation + validation while sale confirmation.......................
    @api.multi
    def action_confirm_pharm(self):
        for ord_line in self.order_line:
            if ord_line.show_lot_visible and not ord_line.lot_id:
                raise UserError(_("Assign Lot to Order line"))
        self.action_confirm()
        for picking in self.picking_ids:
            if picking.state not in ('done', 'cancel'):
                picking.action_confirm()
                picking.action_assign()
                wrong_lots = self.set_so_pack_operation_lot(picking)
                if not wrong_lots:
                    picking.action_done()
                # res_dict = picking.button_validate()
                # wizard = self.env[(res_dict.get('res_model'))].browse(res_dict.get('res_id'))
                # wizard.process()
        self._cr.commit()
        self.action_invoice_create()
        if self.is_pharmacy:
            invoices = self.mapped('invoice_ids')
            for inv in invoices:
                for inv_line in inv.invoice_line_ids:
                    inv_line._compute_price()
                inv._compute_amount()
                inv.write({'is_pharmacy': True})
        for invoice in self.invoice_ids:
            if invoice.state == 'draft':
                invoice.action_invoice_open()
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('pharmacy_management.pharmacy_invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_reopen(self):
        count = False
        if self.date_order:
            if self.date_order == date.today():
                count = True
            else:
                if self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu') or \
                        self.env.user.has_group('pharmacy_management.group_pharmacy_manager'):
                    count = True
                else:
                    count = False
        else:
            count = True
        if count:
            return {
                'name': _('Enter Reopen Reason'),
                'type': 'ir.actions.act_window',
                'res_model': 'sale.reopen',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': None
            }
        else:
            raise UserError(_(
                'You are not allowed to do this. Please contact system administrator !!'))


    def set_so_pack_operation_lot(self, picking):
        """Set Serial/Lot number in pack operations to mark the pack operation done."""
        StockProductionLot = self.env['stock.production.lot']
        sale_line_obj = self.env['sale.order.line']
        has_wrong_lots = False
        for del_move in picking.move_lines:
            del_move.move_line_ids.unlink()
        for move in picking.move_lines:
            picking_type = picking.picking_type_id
            # lots_necessary = True
            if picking_type:
                if not picking_type.use_existing_lots:
                    picking_type.write({'use_existing_lots':True})
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
                    stock_production_lot = StockProductionLot.search([('id', '=', lot_id), ('product_id', '=', move.product_id.id)])
                    sale_order_line = sale_line_obj.search([('lot_id', '=', lot_id),('order_id', '=', self.id), ('product_id', '=', move.product_id.id)])
                    if stock_production_lot and sale_order_line:
                        if stock_production_lot.product_id.tracking == 'lot':
                            # if a lot nr is set through the frontend it will refer to the full quantity
                            qty = sale_order_line[0].product_uom_qty
                        else:
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
            if not pack_lots:
                move.quantity_done = qty_done
        return has_wrong_lots

    # .......................Sale cancellation - Invoice and delivery cancellation.......................

    def _prepare_move_default_values(self, res, return_line_move_id, return_line_quantity, return_line_product_id, new_picking):
        vals = {
            'product_id': return_line_product_id.id,
            'product_uom_qty': return_line_quantity,
            'picking_id': new_picking.id,
            'state': 'draft',
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
                vals = self._prepare_move_default_values(res, return_line_move_id, return_line_quantity, return_line_product_id, new_picking)
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
        wrong_lots = self.set_so_pack_operation_lot(new_picking)
        if not wrong_lots:
            new_picking.action_done()
        # res_dict = new_picking.button_validate()
        # wizard = self.env[(res_dict.get('res_model'))].browse(res_dict.get('res_id'))
        # wizard.process()
        return new_picking, picking_type_id

    def create_returns(self, res):
        for wizard in self:
            new_picking_id, pick_type_id = wizard._create_returns(res)
            return new_picking_id

    def pharm_delivery_cancel(self, picking):
        if picking:
            if picking.state != 'done':
                picking.action_cancel()
            else:
                res = {}
                move_dest_exists = False
                product_return_moves = []
                res.update({'picking_id': picking})
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

    def pharm_invoice_cancel(self, sale_invoice_id):
        if sale_invoice_id.state == 'draft':
            sale_invoice_id.write({'move_name': False})
        if sale_invoice_id.state == 'open' and not sale_invoice_id.payment_ids:
            sale_invoice_id.modify_invoice()
        if sale_invoice_id.state == 'open' and sale_invoice_id.payment_ids:
            for paymt in sale_invoice_id.payment_ids:
                paymt.cancel()
                # paymt.delete_payment()
            sale_invoice_id.modify_invoice()
        if sale_invoice_id.state == 'cancel':
            sale_invoice_id.action_invoice_draft()
        if sale_invoice_id.state == 'paid':
            for paymt in sale_invoice_id.payment_ids:
                paymt.cancel()
                # paymt.delete_payment()
            sale_invoice_id.modify_invoice()
        sale_invoice_id.write({'state': 'draft', 'move_name': False})
        sale_invoice_id.action_invoice_cancel()

    @api.multi
    def action_cancel(self):
        # ........Invoice cancellation.........
        for inv in self.mapped('invoice_ids'):
            self.pharm_invoice_cancel(inv)
        # ........Stock cancellation/return.........
        for deliv in self.mapped('picking_ids'):
            self.pharm_delivery_cancel(deliv)
        self.write({'state': 'cancel'})

    # .......................New view for Smart button for invoices in sale order.......................
    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            if self.is_pharmacy:
                action['views'] = [(self.env.ref('pharmacy_management.pharmacy_invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
