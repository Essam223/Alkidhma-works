# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError


class ProjectShutdown(models.Model):
    _name = "project.shutdown"
    _rec_name = 'shutdown_date'

    restrict_login = fields.Boolean('Restrict login', default=True)
    shutdown_date = fields.Date('Shutdown date', required=False)