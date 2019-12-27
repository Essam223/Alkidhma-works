# -*- coding: utf-8 -*-
{
    'name': 'HR Payslip Enhanced',
    'version': '10.0.1.0.0',
    'summary': 'HR Management',
    'description': """ 
        """,
    'category': 'Human Resources',
    'author': 'Al Kidhma Group',
    'website': "",
    'company': '',
    'depends': [
                'hr_payroll',
                'hr_payroll_account',
                'hr_complete_solution',
                'update_invoice_payment',
                ],
    'data': [
        "security/ir.model.access.csv",
        'views/account_payment.xml',
        'views/hr_payslip.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
