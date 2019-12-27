# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError


class MedicalPhysician(models.Model):
    _inherit = "medical.physician"

    manage_clinic_location = fields.Boolean(string='Manage Clinic location')
    clinic_location_id = fields.Many2one('stock.location', string='Clinic location',
                                             domain="[('usage', '=', 'internal')]")
