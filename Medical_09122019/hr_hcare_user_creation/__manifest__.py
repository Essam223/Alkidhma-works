# -*- coding: utf-8 -*-
{
    'name': 'HR Hcare User Creation',
    'version': '10.0.1.0.0',
    'summary': 'HR Management',
    'description': """ 
        """,
    'category': 'Human Resources',
    'author': 'Al Kidhma Group',
    'depends': [
                'pragtech_dental_management',
                'hr',
                'hr_holidays',
                'hr_attendance',
                'hr_payroll',
                ],
    'data': [
        'views/user_creation.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
