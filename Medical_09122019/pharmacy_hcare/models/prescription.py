from odoo import api, fields, models, tools, _


class PrescriptionLine(models.Model):
    _inherit = "prescription.line"

    qty_available = fields.Float(related='medicine_id.qty_available', string='Quantity Available')