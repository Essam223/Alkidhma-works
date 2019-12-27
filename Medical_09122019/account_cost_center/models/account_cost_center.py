# Copyright 2015-2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class AccountCostCenter(models.Model):
    _name = 'account.cost.center'
    _description = 'Account Cost Center'

    name = fields.Char(string='Title', required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id
    )

    @api.multi
    @api.depends('name', 'company_id')
    def name_get(self):
        result = []
        for cost_center in self:
            if self.env.user.has_group('base.group_multi_company'):
                name = cost_center.company_id.name + ' - ' + cost_center.name
            else:
                name = cost_center.name
            result.append((cost_center.id, name))
        return result

