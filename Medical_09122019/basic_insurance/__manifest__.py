# -*- coding: utf-8 -*-
{
    'name': 'Basic Insurance',
    'version': '1.1',
    'category': 'Accounting',
    'author': 'Al Kidhma Group',
    'website': '',
    'license': 'AGPL-3',
    'depends': ['pragtech_dental_management'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/res_config_views.xml',
        'views/insurance.xml',
        'views/dental.xml',
        'views/invoice.xml',
        'wizard/income_by_insurance_company.xml',
        'wizard/claim_wizard.xml',
        'report/reports.xml',
        'report/report_income_by_insurance_company.xml',
        'report/claim_report_temp.xml',
        'report/account_invoice_report_view.xml',
    ],

    'demo': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}
