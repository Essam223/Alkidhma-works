# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class TreatmentInvoice(models.Model):
    _inherit = 'treatment.invoice'

    qty = fields.Integer('No.of Sessions', required=True, default=1)
