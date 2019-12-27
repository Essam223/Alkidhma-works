# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MedicalOccupation(models.Model):
    _name = "medical.occupation"
    _description = "Occupation / Job"

    name = fields.Char('Occupation', size=128, required=True)
    code = fields.Char('Code', size=64)

    _sql_constraints = [
        ('occupation_name_uniq', 'unique(name)', 'The Name must be unique !'),
    ]