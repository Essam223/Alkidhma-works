# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError


class Product(models.Model):
    _inherit = "product.template"

    is_consumable = fields.Boolean('Is Consumable')
    consumable_ids = fields.One2many('product.consumables', 'product_tmpl_id')

    @api.multi
    @api.onchange('name')
    def check_prod_name(self):
        self.set_access_to_edit_consumables()

    def set_access_to_edit_consumables(self):
        for rec in self:
            if self.env.user.has_group('service_consumable.group_consumable_mgmnt_manager_menu'):
                rec.access_to_edit_consumables = True

    access_to_edit_consumables = fields.Boolean(compute=set_access_to_edit_consumables, string='Edit Consumables?')
