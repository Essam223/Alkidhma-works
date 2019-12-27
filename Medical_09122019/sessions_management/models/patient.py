# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class MedicalAppointment(models.Model):
    _inherit = 'medical.patient'

    session_ids = fields.One2many('medical.session', 'patient_id', 'Sessions')
