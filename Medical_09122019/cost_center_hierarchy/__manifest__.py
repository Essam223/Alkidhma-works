# -*- coding: utf-8 -*-
{
    'name': 'Cost Center Hierarchy',
    'version': '10.0',
    'category': '',
    'sequence': 2,
    'summary': '',
    'description': """
    """,
    'author': 'Al Kidhma Group',
    'depends': ['pragtech_dental_management', 'account_cost_center'],
    'data': [
        'security/ir.model.access.csv',
        'security/multi_company_security.xml',
        'views/physician.xml',
        'views/department.xml',
        'views/cost_center.xml',
        'views/company.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
