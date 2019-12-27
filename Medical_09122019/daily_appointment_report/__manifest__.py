# -*- encoding: utf-8 -*-
{

    'name': 'Appointment Daily Book Report',
    'version': '11.0',
    'author': 'Al Kidhma Group',
    'sequence': 2,
    'category': 'Generic Modules/Others',
    'depends': ['pragtech_dental_management',
                ],
    'description': """
This modules includes Appointment Daily Book Report
""",
    'website': '',
    "data": [
        'reports/report.xml',
        'reports/report_doctor_daily_appointment.xml',
        'wizard/doctor_daily_appointment_report.xml',
    ],
    'active': False,
    'images': [],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
