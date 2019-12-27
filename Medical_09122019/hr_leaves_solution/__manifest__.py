# -*- coding: utf-8 -*-
{
    'name': 'Leave Management',
    'version': '10.0.2.0.0',
    'summary': 'Manage Leave',
    'description': """
        Helps you to manage Leave.\n
        HR Leave extension functionality\n
        
        """,
    'category': 'Human Resources',
    'author': 'Al Kidhma Group',
    'website': "",
    'company': '',
    'depends': [
        'base', 'hr_holidays', 'hr_payroll'
    ],
    'data': [
        'data/salary_rule_unpaid.xml',
        'wizard/leave_extension.xml',
        'wizard/salary_report_wizard.xml',
        'views/reports.xml',
        'views/salary_report.xml',
        'views/report_payslip_templates.xml',
        'views/hr_holidays_status.xml',
        'views/leave.xml',
    ],
    'demo': [],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
