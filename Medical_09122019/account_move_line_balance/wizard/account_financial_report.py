# -*- coding: utf-8 -*-
from odoo import fields, models


class account_report_partner_ledger(models.TransientModel):
    _inherit = "accounting.report"

    debit_credit = fields.Boolean(string='Display Debit/Credit Columns', default=True,
                                  help="This option allows you to get more details about the way your balances are "
                                       "computed. Because it is space consuming, we do not allow to use it while doing "
                                       "a comparison.")
    show_description = fields.Boolean(string='Display Description', default=True,
                                  help="This option allows you to get more details about the way your Journal entries are "
                                       "computed. Because it is space consuming, we do not allow to use it while doing "
                                       "a comparison.")

    def _print_report(self, data):
        data['form'].update(self.read(['show_description', 'date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter', 'target_move'])[0])
        return self.env.ref('account.action_report_financial').report_action(self, data=data, config=False)



