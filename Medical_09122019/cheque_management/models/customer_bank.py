# -*- coding: utf-8 -*-

from odoo import fields, models


class CustomerBank(models.Model):
    _name = "customer.bank"

    name = fields.Char(string='Bank Name', required=True)
    _sql_constraints = [('name_uniq', 'unique (name)', 'The name of the bank must be unique !')]
