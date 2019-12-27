from odoo import api, models, fields


class AccountCostCenter(models.Model):
    _inherit = "account.cost.center"

    department_ids = fields.One2many('medical.department', 'cost_center_id', string='Department')
