# -*- coding: utf-8 -*-

from odoo import fields, models


class ReturnReason(models.Model):
    _name = "return.reason"

    name = fields.Char(string='Reason', required=True)
    comment_required = fields.Boolean(string="Comment Required ?")
    _sql_constraints = [('name_uniq', 'unique (name)', 'The reason must be unique !')]
