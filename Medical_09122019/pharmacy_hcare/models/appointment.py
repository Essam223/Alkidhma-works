# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MedicalAppointment(models.Model):
    _inherit = "medical.appointment"

    sale_id = fields.Many2one('sale.order', string='Sale')

    def _compute_sale(self):
        for order in self:
            sales = self.env['sale.order'].search([('appt_prescription_id', '=', self.id)])
            order.sale_ids = sales
            order.sale_count = len(sales)

    sale_count = fields.Integer(compute="_compute_sale", string='# of Sales', copy=False, default=0, store=False)
    sale_ids = fields.Many2many('sale.order', compute="_compute_sale", string='Sales', copy=False,
                                   store=False)

    @api.multi
    def print_drug_label(self):
        datas = {'ids': self.ids}
        values = self.env.ref('pharmacy_hcare.drug_print').report_action(self, data=datas)
        return values

    @api.multi
    def action_view_sales(self):
        domain = []
        res_id = []
        view_id = self.env.ref('pharmacy_management.pharmacy_sale_form').id
        context = self._context.copy()
        sales = self.sale_ids
        if len(sales) > 1:
            domain = [('id', 'in', sales.ids)]
            view_id = self.env.ref('sale.view_order_tree').id
        elif len(sales) == 1:

            res_id = sales.ids[0]
        return {
            'name': 'Sale Order',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'sale.order',
            'view_id': view_id,
            'domain': domain,
            'type': 'ir.actions.act_window',
            'res_id': res_id,
            'target': 'current',
            'context': context,
        }

    def Convert_to_Order(self):
        sale_vals = {
            'partner_id': self.patient.name.id,
            'is_pharmacy': True,
            'appt_prescription_id': self.id,
            'currency_id': self.env.user.currency_id.id,
        }
        order = self.env['sale.order'].create(sale_vals)
        for prescptions in self.prescription_ids:
            sale_line_vals = {
                'name': prescptions.note or '/',
                'order_id': order.id,
                'price_unit': prescptions.medicine_id.lst_price,
                'product_id': prescptions.medicine_id.id,
                'product_uom': prescptions.medicine_id.uom_id.id,
                'product_uom_qty': 1,
            }
            self.env['sale.order.line'].create(sale_line_vals)
        view_id = self.env.ref('pharmacy_management.pharmacy_sale_form').id
        context = self._context.copy()
        return {
            'name': 'Sale Order',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'sale.order',
            'view_id': view_id,
            'domain': [],
            'type': 'ir.actions.act_window',
            'res_id': order.id,
            'target': 'current',
            'context': context,
        }