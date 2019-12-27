# -*- coding: utf-8 -*-
from . import models
from . import wizard
from odoo import api, SUPERUSER_ID, _


def _create_loan_journal_and_accounts(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    user_company = env['res.users'].browse(SUPERUSER_ID).company_id.id
    JournalObj = env['account.journal']
    for comp in env['res.company'].search([('id', '!=', user_company)]):
        res = [{'type': 'bank', 'name': _('HR Loan'), 'code': 'LOAN',
                'company_id': comp.id, }]
        for vals_journal in res:
            JournalObj.create(vals_journal)

