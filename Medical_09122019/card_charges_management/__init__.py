from . import models
from . import wizard

from odoo import api, SUPERUSER_ID, _


def _create_journal_and_accounts(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    user_company = env['res.users'].browse(SUPERUSER_ID).company_id.id
    JournalObj = env['account.journal']
    for comp in env['res.company'].search([('id', '!=', user_company)]):
        res = [{'type': 'bank', 'name': _('Card Reconciliation'), 'code': 'CR',
                'company_id': comp.id, 'show_on_dashboard': True, },
               {'type': 'bank', 'name': _('Card Charges'), 'code': 'CC',
                'company_id': comp.id, 'show_on_dashboard': True, }]
        for vals_journal in res:
            JournalObj.create(vals_journal)
