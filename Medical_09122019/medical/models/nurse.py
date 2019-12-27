# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class MedicalNurse(models.Model):
    _name = "medical.nurse"
    _rec_name = 'nurse'

    @api.model
    def _get_nurses_id(self):
        return [('groups_id', '=', self.env.ref('medical.group_dental_nurse_menu').id)]

    nurse = fields.Many2one('res.users', 'Nurse', domain=_get_nurses_id, required=True)

    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')

    company_id = fields.Many2one('res.company', 'Company', index=True, default=_default_company)

