# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    _sql_constraints = [
            ('patient_id_uniq', 'check(1=1)', 'The Patient ID already exists'),
            ('patient_id_unique', 'unique(patient_id, company_id)', 'The Patient ID must be unique per company!'),
            ]