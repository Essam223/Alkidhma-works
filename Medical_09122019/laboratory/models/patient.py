# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class MedicalPatient(models.Model):
    _inherit = 'medical.patient'

    lab_ids = fields.One2many('lab.request', 'patient_id', 'Lab Orders')
