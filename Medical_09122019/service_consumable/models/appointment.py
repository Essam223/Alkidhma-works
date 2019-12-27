# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError


class MedicalAppointment(models.Model):
    _inherit = "medical.appointment"

    @api.multi
    @api.onchange('name', 'patient')
    def check_prod_name(self):
        self.set_access_to_edit_consumables()

    def set_access_to_edit_consumables(self):
        for rec in self:
            if self.env.user.has_group('service_consumable.group_consumable_mgmnt_manager_menu'):
                rec.access_to_edit_consumables = True

    access_to_edit_consumables = fields.Boolean(compute=set_access_to_edit_consumables, string='Edit Consumables?')

    def create_consumables(self):
        for appt in self:
            appt.consumable_ids.unlink()
            for t_inv in appt.treatment_ids:
                if t_inv.description.type == 'service':
                    for consumable in t_inv.description.consumable_ids:
                        if consumable.consu_product_id.type == 'product':
                            vals = {'product_tmpl_id': consumable.product_tmpl_id.id,
                                    'consu_product_id': consumable.consu_product_id.id,
                                    'quantity': consumable.quantity,
                                    'appt_id': appt.id,
                                    'payment_line_id': t_inv.id}
                            self.env['appt.consumables'].create(vals)

    reason_stock_reversal = fields.Text('Reason for Stock Reversal', track_visibility='onchange')
    consumable_ids = fields.One2many('appt.consumables', 'appt_id', string='Consumables')
    delivery_id = fields.Many2one('stock.picking', 'Delivery')
    delivery_count = fields.Integer(string='# of Deliveries', compute='_get_delivered', readonly=True)
    delivery_ids = fields.Many2many("stock.picking", string='Deliveries', compute="_get_delivered", readonly=True,
                                   copy=False)

    @api.depends('name')
    def _get_delivered(self):
        for appt in self:
            delivery_ids = self.env['stock.picking'].search([('appt_id', '=', appt.id)])
            appt.update({
                'delivery_count': len(set(delivery_ids.ids)),
                'delivery_ids': delivery_ids.ids,
            })

    @api.multi
    def action_view_delivery(self):
        deliveries = self.mapped('delivery_ids')
        action = self.env.ref('stock.action_picking_tree').read()[0]
        pick_out = self.env.ref('stock.picking_type_out').id
        # action['context'] = {'search_default_picking_type_id': [pick_out], 'default_picking_type_id': pick_out}
        action['context'] = {}
        if len(deliveries) > 1:
            action['domain'] = [('id', 'in', deliveries.ids)]
        elif len(deliveries) == 1:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = deliveries.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def stock_update(self):
        consumable_ids = self.consumable_ids
        treatment_product_list = [treatment for treatment in self.treatment_ids if treatment.description.type == 'product']
        stock_vals = {}
        stock_line_vals = []
        deliv_id = False
        patient_brw = self.patient
        partner_brw = patient_brw.name
        if consumable_ids or treatment_product_list:
            company = self.env.user.company_id
            pick_out = self.env.ref('stock.picking_type_out').id
            if not pick_out:
                pick_out = self.env['stock.picking.type'].search(
                    [('warehouse_id.company_id', '=', company.id), ('code', '=', 'outgoing')],
                    limit=1,
                )
            if not pick_out:
                raise UserError(_('Create Outgoing Picking Type.'))
            pick_out_browse = self.env['stock.picking.type'].browse(pick_out)
            source_location = False
            if self.doctor.manage_clinic_location:
                source_location = self.doctor.clinic_location_id
                if not self.doctor.clinic_location_id:
                    raise UserError(_('Define Clinic location for Doctor: %s.' % (self.doctor.name.name)))
            if not source_location:
                if not pick_out_browse.default_location_src_id:
                    raise UserError(_('Define Source location for Picking Type: %s.' % (pick_out_browse.name)))
                source_location = pick_out_browse.default_location_src_id
            if not pick_out_browse.default_location_dest_id:
                raise UserError(_('Define Destination location for Picking Type: %s.' % (pick_out_browse.name)))
            for each in consumable_ids:
                each_line = [0, False]
                product_dict = {}
                product_dict['product_id'] = each.consu_product_id.product_variant_ids.id
                product_dict['name'] = each.consu_product_id.product_variant_ids.name
                product_dict['product_uom'] = each.consu_product_id.product_variant_ids.uom_id.id
                product_dict['product_uom_qty'] = each.quantity
                product_dict['ordered_qty'] = each.quantity
                product_dict['location_id'] = source_location.id
                product_dict['location_dest_id'] = pick_out_browse.default_location_dest_id.id
                product_dict['company_id'] = company.id
                each_line.append(product_dict)
                stock_line_vals.append(each_line)
            for each in treatment_product_list:
                each_line = [0, False]
                product_dict = {}
                product_dict['product_id'] = each.description.id
                product_dict['name'] = each.description.name
                product_dict['product_uom'] = each.description.uom_id.id
                product_dict['product_uom_qty'] = 1
                product_dict['ordered_qty'] = 1
                product_dict['location_id'] = source_location.id
                product_dict['location_dest_id'] = pick_out_browse.default_location_dest_id.id
                product_dict['company_id'] = company.id
                each_line.append(product_dict)
                stock_line_vals.append(each_line)
            # Creating Delivery dictionary
            stock_vals['scheduled_date'] = self.appointment_sdate
            stock_vals['origin'] = self.name
            stock_vals['partner_id'] = partner_brw.id
            stock_vals['picking_type_id'] = pick_out_browse.id
            stock_vals['move_type'] = 'direct'
            stock_vals['company_id'] = company.id
            stock_vals['location_id'] = source_location.id
            stock_vals['location_dest_id'] = pick_out_browse.default_location_dest_id.id
            stock_vals['move_lines'] = stock_line_vals
            stock_vals['appt_id'] = self.id
            deliv_id = self.env['stock.picking'].create(stock_vals)
            deliv_id.action_confirm()
            deliv_id.action_assign()
            res_dict = deliv_id.button_validate()
            wizard = self.env[(res_dict.get('res_model'))].browse(res_dict.get('res_id'))
            wizard.process()
        vals = {}
        if deliv_id:
            vals['delivery_id'] = deliv_id.id
        return self.write(vals)

    @api.multi
    def stock_reverse(self):
        # self.delivery_id.action_cancel()
        contextt = {}
        contextt['default_appt_id'] = self.id
        appt = self
        msg = ""
        delivery_id = appt.delivery_id
        if delivery_id:
            msg = "Upon Confirmation , "
            if delivery_id.state != 'done':
                msg += "System will Cancel an Delivery Order "
            else:
                msg += "System will Create a Return Order for Delivery Order "
            if delivery_id.name:
                msg += _("(") + " %s " % (delivery_id.name) + _(")")
        contextt['default_warning_msg'] = msg
        return {
            'name': _('Enter Stock Reversal Reason '),
            'view_id': self.env.ref('service_consumable.view_stock_reversal_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'stock.reversal',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }