# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportFinancial(models.AbstractModel):
    _inherit = 'report.account.report_financial'

    def _compute_account_balance(self, accounts, dataa):
        """ compute the balance, debit and credit for the provided accounts
        """
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        res = {}
        for account in accounts:
            res[account.id] = dict.fromkeys(mapping, 0.0)
        if accounts:
            tables, where_clause, where_params = self.env['account.move.line']._query_get()
            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                       " FROM " + tables + \
                       " WHERE account_id IN %s " \
                            + filters + \
                       " GROUP BY account_id"
            params = (tuple(accounts._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                res[row['id']] = row
        for key, value in res.items():
            prev_move_line = self.env['account.move.line'].search([('account_id', '=', key),
                                                                   ('date', '<=', dataa['date_from']),
                                                                   ('move_id.state', '=', 'posted'),
                                                                   ])
            total_debit = 0.0
            total_credit = 0.0
            for move_line in prev_move_line:
                total_debit = total_debit + move_line.debit
                total_credit = total_credit + move_line.credit
            value['opening_balance'] = total_debit - total_credit
        return res

    def _compute_report_balance(self, reports, dataa):
        '''returns a dictionary with key=the ID of a record and value=the credit, debit and balance amount
           computed for this record. If the record is of type :
               'accounts' : it's the sum of the linked accounts
               'account_type' : it's the sum of leaf accoutns with such an account_type
               'account_report' : it's the amount of the related report
               'sum' : it's the sum of the children of this record (aka a 'view' record)'''
        res = {}
        fields = ['credit', 'debit', 'balance', 'opening_balance']
        for report in reports:
            if report.id in res:
                continue
            res[report.id] = dict((fn, 0.0) for fn in fields)
            if report.type == 'accounts':
                # it's the sum of the linked accounts
                res[report.id]['account'] = self._compute_account_balance(report.account_ids, dataa)
                for value in res[report.id]['account'].values():
                    for field in fields:
                        res[report.id][field] += value.get(field)
            elif report.type == 'account_type':
                # it's the sum the leaf accounts with such an account type
                accounts = self.env['account.account'].search([('user_type_id', 'in', report.account_type_ids.ids)])
                res[report.id]['account'] = self._compute_account_balance(accounts, dataa)
                for value in res[report.id]['account'].values():
                    for field in fields:
                        res[report.id][field] += value.get(field)
            elif report.type == 'account_report' and report.account_report_id:
                # it's the amount of the linked report
                res2 = self._compute_report_balance(report.account_report_id, dataa)
                for key, value in res2.items():
                    for field in fields:
                        res[report.id][field] += value[field]
            elif report.type == 'sum':
                # it's the sum of the children of this account.report
                res2 = self._compute_report_balance(report.children_ids, dataa)
                for key, value in res2.items():
                    for field in fields:
                        res[report.id][field] += value[field]
        return res

    def get_account_lines(self, data):
        lines = []
        account_report = self.env['account.financial.report'].search([('id', '=', data['account_report_id'][0])])
        child_reports = account_report._get_children_by_order()
        res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports, data)
        if data['enable_filter']:
            comparison_res = self.with_context(data.get('comparison_context'))._compute_report_balance(child_reports, data)
            for report_id, value in comparison_res.items():
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in comparison_res[report_id].get('account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']

        for report in child_reports:
            vals = {
                'name': report.name,
                'balance': res[report.id]['balance'] * report.sign,
                'opening_balance': res[report.id]['opening_balance'] ,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type or False, #used to underline the financial report balances
            }
            if data['debit_credit']:
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']


            if data['enable_filter']:
                vals['balance_cmp'] = res[report.id]['comp_bal'] * report.sign

            lines.append(vals)
            if report.display_detail == 'no_detail':
                #the rest of the loop is used to display the details of the financial report, so it's not needed here.
                continue

            if res[report.id].get('account'):
                sub_lines = []
                for account_id, value in res[report.id]['account'].items():
                    #if there are accounts to display, we add them to the lines with a level equals to their level in
                    #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
                    #financial reports for Assets, liabilities...)
                    flag = False
                    account = self.env['account.account'].browse(account_id)
                    vals = {
                        'account': account.id,
                        'name': account.code + ' ' + account.name,
                        'balance': value['balance'] * report.sign or 0.0,
                        'opening_balance': value['opening_balance'] or 0.0,
                        'type': 'account',
                        'level': report.display_detail == 'detail_with_hierarchy' and 4,
                        'account_type': account.internal_type,
                    }

                    if data['debit_credit']:
                        vals['debit'] = value['debit']
                        vals['credit'] = value['credit']
                        if not account.company_id.currency_id.is_zero(vals['debit']) or not account.company_id.currency_id.is_zero(vals['credit']):
                            flag = True
                    if not account.company_id.currency_id.is_zero(vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        vals['balance_cmp'] = value['comp_bal'] * report.sign
                        if not account.company_id.currency_id.is_zero(vals['balance_cmp']):
                            flag = True
                    if flag:
                        sub_lines.append(vals)
                        lines += sorted(sub_lines, key=lambda sub_line: sub_line['name'])
                        mapping = {
                            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
                            'debit': "COALESCE(SUM(debit), 0) as debit",
                            'credit': "COALESCE(SUM(credit), 0) as credit",
                        }
                        tables, where_clause, where_params = self.env['account.move.line']._query_get()
                        tables = tables.replace('"', '') if tables else "account_move_line"
                        wheres = [""]
                        if where_clause.strip():
                            wheres.append(where_clause.strip())
                        filters = " AND ".join(wheres)
                        request_1 = "SELECT account_move_line.name as name,account_move_line.partner_id as partner_id," \
                                    "account_move_line.id as a_m_id,account_id as id, " + ', '.join(
                            mapping.values()) + \
                                    " FROM " + tables + \
                                    " WHERE account_id IN %s " \
                                    + filters + \
                                    " GROUP BY a_m_id,name,account_id"
                        accounts_here = self.env['account.account'].search([])
                        params = (tuple(accounts_here._ids),) + tuple(where_params)
                        self.env.cr.execute(request_1, params)
                        a_m_lines = self.env.cr.dictfetchall()
                        if data['show_description']:
                            for a_m_l in a_m_lines:
                                if a_m_l['id'] == vals['account']:
                                    a_m_l['partner_id_name'] = self.env['res.partner'].browse(a_m_l['partner_id']).name
                                    a_m_l['account'] = a_m_l['id']
                                    a_m_l['level'] = 5
                                    a_m_l['type'] = 'a_move_line'
                                    lines.append(a_m_l)
        from collections import OrderedDict
        return OrderedDict((frozenset(item.items()), item) for item in lines).values()