# -*- coding: utf-8 -*-
{
    'name': "Hr Automatic allocation",
    'summary': """ Automatic allocation (Yearly/Monthly)""",
    'description': """
        Automatic process for allocating leaves during each year/month.

 """,
    'author': 'Al Kidhma Group',
    'category': 'Human Resources',
    'version': '1.0.1',
    'depends': [
        'mail', 'hr_holidays', 'hr_contract', 'hr_leaves_solution'
    ],
    'data': [
        'data/cron.xml',
        'views/hr_employee.xml',
        'views/hr_holidays_status.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
