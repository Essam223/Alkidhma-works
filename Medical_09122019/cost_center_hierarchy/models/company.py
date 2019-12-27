from odoo import api, models, fields


class Company(models.Model):
    _inherit = "res.company"

    cost_center_ids = fields.One2many('account.cost.center', 'company_id', string='Cost Centers')
