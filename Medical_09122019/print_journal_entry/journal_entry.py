# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def print_journal(self):
        return self.env.ref('print_journal_entry.act_report_journal_entry').report_action(self)
