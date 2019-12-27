# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    appt_prescription_id = fields.Many2one('medical.appointment', string='Prescription')
