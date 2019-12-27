# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ChartSelection(models.Model):
    _description = "teeth chart selection"
    _name = "chart.selection"

    type = fields.Selection(
        [('universal', 'Universal Numbering System'), ('palmer', 'Palmer Method'), ('iso', 'ISO FDI Numbering System')],
        'Select Chart Type', default='universal')
