from odoo import api, models, fields


class Company(models.Model):
    _inherit = "res.company"

    watermark_image = fields.Binary("Report Watermark")
