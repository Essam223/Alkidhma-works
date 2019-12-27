# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.multi
    @api.depends('name', 'code', 'company_id')
    def name_get(self):
        result = []
        for account in self:
            if self.env.user.has_group('base.group_multi_company'):
                name = account.code + ' ' + account.company_id.name + ' ' + account.name
            else:
                name = account.code + ' ' + account.name
            result.append((account.id, name))
        return result