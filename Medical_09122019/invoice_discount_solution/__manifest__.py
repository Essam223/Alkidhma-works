# -*- coding: utf-8 -*-
{
    'name': 'Invoice Discount',
    'version': '11.0.1.0.0',
    'category': 'Invoice Discount',
    'summary': "Fixed and Percentage Discount on Invoice and Invoice Lines",
    'author': 'Al Kidhma Group',
    'company': 'Al Kidhma Group',
    'website': 'http://www.alkidhmagroup.com',
    'description': """
""",
    'depends': [
                'account',
                ],
    'data': [
        'views/account_invoice_view.xml',
        'res_config_views.xml',
    ],
    'demo': [
    ],
    'images': [],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
