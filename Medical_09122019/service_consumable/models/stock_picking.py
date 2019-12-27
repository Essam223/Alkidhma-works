# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    appt_id = fields.Many2one("medical.appointment", 'Appointment', readonly=True)
