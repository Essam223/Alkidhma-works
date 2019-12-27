from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class StockReversal(models.TransientModel):
    _name = 'stock.reversal'

    reason_stock_reversal = fields.Text('Reason for Stock Reversal', required=True)
    warning_msg = fields.Text('Warning')
    appt_id = fields.Many2one('medical.appointment', 'Appointment', required=True)

    def do_delivery_act_msg(self, new_picking_id, appt_delivery_id, appt):
        if appt_delivery_id.state != 'done':
            msg = "<b> Cancelled Delivery Order: </b>"
        else:
            msg = "<b> Created a Return Order </b>"
            if new_picking_id:
                msg += _("(") + " %s " % (new_picking_id.name) + _(")")
            msg += "<b> for Delivery Order: </b>"
        if appt_delivery_id.name:
            msg += _("(") + " %s " % (appt_delivery_id.name) + _(")")
        msg += "</ul>"
        appt.message_post(body=msg)

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
        res_dict = new_picking.button_validate()
        wizard = self.env[(res_dict.get('res_model'))].browse(res_dict.get('res_id'))
        wizard.process()
        return new_picking, picking_type_id

    def create_returns(self, res):
        for wizard in self:
            new_picking_id, pick_type_id = wizard._create_returns(res)
            return new_picking_id

    @api.multi
    def action_confirm(self):
        wizard_vals = self.read()[0]
        if wizard_vals['appt_id']:
            appt = self.env['medical.appointment'].browse(wizard_vals['appt_id'][0])
            picking = appt.delivery_id
            new_picking_id = False
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
                        res.update({'parent_location_id': picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.view_location_id.id or picking.location_id.location_id.id})
                    res.update({'original_location_id': picking.location_id.id})
                    location_id = picking.location_id
                    if picking.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
                        location_id = picking.picking_type_id.return_picking_type_id.default_location_dest_id
                    res['location_id'] = location_id
                    new_picking_id = self.create_returns(res)
            self.do_delivery_act_msg(new_picking_id, appt.delivery_id, appt)
            appt.write({'reason_stock_reversal': wizard_vals['reason_stock_reversal'],'delivery_id':False})
                        # 'state': 'ready'})