# -*- coding: utf-8 -*-
{
    'name': 'Detailed Insurance',
    'version': '1.1',
    'category': 'Accounting',
    'author': 'Al Kidhma Group',
    'website': '',
    'license': 'AGPL-3',
    'depends': ['pragtech_dental_management', 'basic_insurance'],
    'data': [
        'views/insurance.xml',
        'views/dental.xml',
        'views/invoice.xml',
        'wizard/update_copay_wizard.xml',
    ],

    'demo': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}
