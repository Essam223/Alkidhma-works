# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MedicalSpeciality(models.Model):
    _name = "medical.speciality"

    name = fields.Char('Description', size=128, required=True, help="ie, Addiction Psychiatry")
    code = fields.Char('Code', size=128, help="ie, ADP")

    _sql_constraints = [
        ('code_uniq', 'unique (name)', 'The Specialty code must be unique')]
