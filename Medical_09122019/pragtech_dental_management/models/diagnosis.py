# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
# from mock import DEFAULT
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import hashlib
import time
from odoo.exceptions import Warning
import json


class Diagnosis(models.Model):
    _name = 'diagnosis'
    _rec_name = 'code'
    
    code = fields.Char('Code', required=True)
    description = fields.Text('Description', required=True)

    @api.multi
    @api.depends('code', 'description')
    def name_get(self):
        result = []
        for rcd in self:
            name = rcd.code or ''
            if rcd.description:
                name += ' / ' + rcd.description
            result.append((rcd.id, name))
        return result

    @api.model
    def get_all_records(self):
        diagnosis_obj=self.env['diagnosis'].search_read([])
        return diagnosis_obj

    @api.multi
    def get_dignosis_description(self):
        return str(self.description)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', operator, name), ('description', operator, name)]
        pos = self.search(domain + args, limit=limit)
        return pos.name_get()
