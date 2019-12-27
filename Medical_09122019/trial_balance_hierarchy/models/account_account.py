# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountAccount(models.Model):
    _inherit = 'account.account'

    parent_id = fields.Many2one('account.account', 'Parent')
    child_parent_ids = fields.One2many('account.account', 'parent_id', string='Children')

