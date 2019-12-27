from odoo import api, models, fields


class Company(models.Model):
    _inherit = "res.company"

    header_image = fields.Binary("Report Header")
    footer_image = fields.Binary("Report Footer")
