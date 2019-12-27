# -*- coding: utf-8 -*-
import math
import re
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    life_date = fields.Datetime(string='Expiry Date',
                                help='This is the date on which the goods with this Serial Number may '
                                     'become dangerous and must not be consumed.')

    def print_barcode(self):
        if not self.product_id.barcode:
            raise UserError(_('Please generate barcode for the product.'))
        return self.env.ref('pharmacy_management.report_lot_barcode_pdf').report_action(self)