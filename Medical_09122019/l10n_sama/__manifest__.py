# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Accounting - Sama',
    'version': '1.1',
    'category': 'Localization',
    'description': """
This is the base module to manage the medical accounting chart in Odoo.
==============================================================================

Install some generic chart of accounts.
    """,
    'author': 'Al Kidhma Group',
    'depends': [
        'account',
    ],
    'data': [
        'data/l10n_sama_chart_data.xml',
        'data/account_chart_template_data.yml',
        # 'security/account.account.template.csv',

    ],
    'test': [

    ],
    'demo': [

    ],
    'website': 'https://www.odoo.com/page/accounting',
}
