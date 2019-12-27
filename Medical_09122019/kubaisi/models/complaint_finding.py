from odoo import api, fields, models, tools, _


class ClinicalFindings(models.Model):
    _inherit = "complaint.finding"

    image = fields.Binary("Complaints and findings")
