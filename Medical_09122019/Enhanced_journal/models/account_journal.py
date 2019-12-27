# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2004-2008 PC Solutions (<http://pcsol.be>). All Rights Reserved
from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    invoice_journal = fields.Boolean('Use in Invoice Payment')
