# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError
import time


class AccountReportGeneralLedger(models.TransientModel):
    _inherit = "account.report.general.ledger"

    account_ids = fields.Many2many('account.account', 'account_report_general_ledger_account_rel', 'account_id', 'acc_account_id', string='Accounts', required=False)

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update(self.read(['account_ids','initial_balance', 'sortby'])[0])
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env.ref('account.action_report_general_ledger').with_context(landscape=True).report_action(records,
                                                                                                               data=data)


class ReportGeneralLedger(models.AbstractModel):
    _inherit = 'report.account.report_generalledger'

    @api.multi
    def get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))

        init_balance = data['form'].get('initial_balance', True)
        sortby = data['form'].get('sortby', 'sort_date')
        display_account = data['form']['display_account']
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]
        acc_domain=[]
        if data['form'].get('account_ids',False):
            accounts=self.env['account.account'].browse(data['form'].get('account_ids',False))
        else:
            accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        accounts_res = self.with_context(data['form'].get('used_context',{}))._get_account_move_entry(accounts, init_balance, sortby, display_account)
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': accounts_res,
            'print_journal': codes,
        }
        return docargs

