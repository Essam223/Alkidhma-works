# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportTrialBalance(models.AbstractModel):
    _inherit = 'report.account.report_trialbalance'

    def _get_accounts(self, accounts, display_account):
        """ compute the balance, debit and credit for the provided accounts
            :Arguments:
                `accounts`: list of accounts record,
                `display_account`: it's used to display either all accounts or those accounts which balance is > 0
            :Returns a list of dictionary of Accounts with following key and value
                `name`: Account name,
                `code`: Account code,
                `credit`: total amount of credit,
                `debit`: total amount of debit,
                `balance`: total amount of balance,
        """

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"','')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
                   " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        account_res = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['is_root'] = 0
            if not account.parent_id:
                res['is_root'] = 1
            res['account_id'] = account
            res['name'] = account.name
            if account.id in account_result:
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
            if display_account == 'movement' and (not currency.is_zero(res['debit']) or not currency.is_zero(res['credit'])):
                account_res.append(res)
        ami = {}
        for account_rec in account_res:
            for a_res in account_res:
                if a_res['account_id'].id == account_rec['account_id'].id:
                    ami = a_res
            # if account_rec['account_id'].id == 53 or account_rec['account_id'].id == 66:
            child_ids = self._get_children_accounts(account_rec['account_id'].id)
            child_ids = list(dict.fromkeys(child_ids))
            if child_ids:
                for child in child_ids:
                    self._process_child(accounts,display_account, child, account_rec['account_id'].id, account_res, ami)
            else:
                self._process_child(accounts, display_account, account_rec['account_id'].id, account_rec['account_id'].id, account_res, ami)
        return account_res

    def _process_child(self, accounts, disp_acc, child, parent, account_res, ami):
        if child != parent:
            for a_res in account_res:
                if a_res['account_id'].id == child:
                    ami['credit'] += a_res['credit']
                    ami['debit'] += a_res['debit']
                    ami['balance'] += a_res['balance']

    def _get_children_accounts(self, account_id):
        #this function search for all the children (recursively) of the given account ids
        ids2 = []
        for children in self.env['account.account'].search([('parent_id', 'child_of', account_id)]):
            ids2.append(children.id)
        ids3 = []
        for rec in self.env['account.account'].browse(account_id):
            for child in rec.child_parent_ids:
                ids3.append(child.id)
        if ids3:
            ids3 = self._get_children_accounts(ids3)
        return ids2 + ids3

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        display_account = data['form'].get('display_account')
        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account)

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': account_res,
        }
