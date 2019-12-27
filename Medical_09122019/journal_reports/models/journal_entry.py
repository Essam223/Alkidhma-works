# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class JournalEntry(models.TransientModel):
    _name = 'journal.entry.wizard'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    posted = fields.Boolean('Posted entries only')

    @api.onchange('start_date', 'end_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.multi
    def generate_report(self):
        data = {'start_date': self.start_date, 'end_date': self.end_date, 'posted': self.posted}
        return self.env.ref('journal_reports.report_journal_entry').report_action(self, data=data)


class ReportJournalEntry(models.AbstractModel):
    _name = 'report.journal_reports.report_journal_entry_pdf'

    @api.model
    def get_move_details(self, start_date=False, end_date=False, posted=False):
        lst_search = []
        if start_date:
            lst_search.append(('date', '>=', start_date))
        if end_date:
            lst_search.append(('date', '<=', end_date))
        if posted:
            lst_search.append(('state', '=', 'posted'))
        move_ids = self.env['account.move'].search(lst_search)
        lines = move_ids

        return {
            'start_date': start_date,
            'end_date': end_date,
            'posted': posted,
            'lines': lines,
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_move_details(data['start_date'],
                                          data['end_date'],
                                          data['posted']))
        return data
