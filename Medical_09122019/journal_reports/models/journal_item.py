# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class JournalItem(models.TransientModel):
    _name = 'journal.item.wizard'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    account_id = fields.Many2one('account.account', 'Account')

    @api.onchange('start_date', 'end_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.multi
    def generate_report(self):
        data = {'start_date': self.start_date, 'end_date': self.end_date, 'account_id': self.account_id.id}
        return self.env.ref('journal_reports.report_journal_item').report_action(self, data=data)


class ReportJournalItem(models.AbstractModel):
    _name = 'report.journal_reports.report_journal_item_pdf'

    @api.model
    def get_move_details(self, start_date=False, end_date=False, account_id=False):
        lst_search = []
        acc_name = False
        if start_date:
            lst_search.append(('date', '>=', start_date))
        if end_date:
            lst_search.append(('date', '<=', end_date))
        if account_id:
            acc_name = self.env['account.account'].search([('id', '=',account_id)]).name
            lst_search.append(('account_id', '=', account_id))
        move_ids = self.env['account.move.line'].search(lst_search)
        lines = move_ids
        return {
            'start_date': start_date,
            'end_date': end_date,
            'account_id': acc_name,
            'lines': lines,
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_move_details(data['start_date'],
                                                 data['end_date'],
                                                 data['account_id']))
        return data
