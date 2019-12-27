# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    card_reconcile = fields.Boolean("Card Reconciled?", readonly=True)
    card_reconcile_id = fields.Many2one('card.charges', 'Reconcile Record', readonly=True)
    line_date = fields.Date('Date', compute='_get_line_date', store=True)

    @api.depends('date')
    def _get_line_date(self):
        for rcd in self:
            if rcd.date:
                if len(rcd.date) < 15:
                    rcd_date = datetime.strptime(rcd.date, "%Y-%m-%d")
                else:
                    rcd_date = datetime.strptime(rcd.date, "%Y-%m-%d %H:%M:%S")
                rcd.line_date = rcd_date.date()
            else:
                rcd.line_date = False

