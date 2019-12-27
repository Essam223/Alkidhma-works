# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class MedicalAppointment(models.Model):
    _inherit = 'medical.appointment'

    patient_file_no = fields.Char('Patient ID', size=64, track_visibility='onchange', readonly=1,
                                  related='patient.patient_id')