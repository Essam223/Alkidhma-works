# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import hashlib
import time
from odoo.exceptions import Warning
from ast import literal_eval
import base64


class PatientNationality(models.Model):
    _name = "patient.nationality"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
