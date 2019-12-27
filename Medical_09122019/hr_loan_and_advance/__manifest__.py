# -*- coding: utf-8 -*-
{
    'name': 'Loan and Advance Management',
    'version': '10.0.2.0.0',
    'summary': 'Manage Loan and Advance Requests',
    'description': """
        Helps you to manage Loan and Advance Requests of Employees.\n
        HR Loan Approval functionality\n
        HR Loan based on Duration (No of Installments)\n
        
        """,
    'category': 'Human Resources',
    'author': 'Al Kidhma Group',
    'website': "",
    'company': '',
    'depends': [
        'base', 'hr_payroll', 'hr', 'account_invoicing',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'report/report.xml',
        'data/mail_template_data.xml',
        'data/loan_accounts.xml',
        'data/hr_loan_seq.xml',
        'data/salary_rule_loan.xml',
        'wizard/pay_manually.xml',
        'wizard/loan_extension.xml',
        'views/hr_loan.xml',
        'report/report_loan.xml',
    ],
    'demo': [],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
    'post_init_hook': '_create_loan_journal_and_accounts',
}
