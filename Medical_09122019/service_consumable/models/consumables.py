# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError


class ProductConsumables(models.Model):
    _name = "product.consumables"

    consu_product_id = fields.Many2one('product.template', string='Consumable Product',
                                       required=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template')
    quantity = fields.Float(required=True, default=1)


class ApptConsumables(models.Model):
    _name = "appt.consumables"

    product_tmpl_id = fields.Many2one('product.template', string='Treatment', domain="[('type', '=', 'service')]")
    consu_product_id = fields.Many2one('product.template', string='Consumable', domain="[('type', '!=', 'service')]",
                                       required=True)
    quantity = fields.Float(required=True)
    appt_id = fields.Many2one('medical.appointment', 'Appointment', required=True)
    payment_line_id = fields.Many2one('treatment.invoice', 'Payment Line')
