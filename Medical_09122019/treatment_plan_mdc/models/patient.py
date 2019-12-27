# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import base64


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    teeth_treatment_ids = fields.One2many('medical.teeth.treatment', 'patient_id', 'Operations', readonly=False)
