# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class MedicalPhysician(models.Model):
    _inherit = "medical.physician"

    dental = fields.Boolean('Dental', default=False)