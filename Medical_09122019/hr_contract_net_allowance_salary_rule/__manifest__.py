# -*- coding: utf-8 -*-
{
    'name': 'HR Contract NET Allowance Salary rule',
    'version': '10.0.1.0.0',
    'summary': 'HR Management',
    'description': """ 
        """,
    'category': 'Human Resources',
    'author': 'Al Kidhma Group',
    'website': "",
    'company': '',
    'depends': [
                'hr_enhanced_payslip',
                'hr_multi_employee_contract',

                ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract.xml',
        'views/employee_form_contract.xml',
        'views/multi_employee_contract.xml',
        'hr_payroll_demo.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
    'demo': ['hr_payroll_demo.xml'],
}
