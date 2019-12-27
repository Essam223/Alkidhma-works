# -*- coding: utf-8 -*-
{
    'name': 'Vertical Resources in Calendar View',
    'version': '11.0.1.0.0',
    'summary': '',
    'category': 'Reporting',
    'author': 'Al Kidhma Group',
    'company': '',
    'maintainer': '',
    'depends': ['web', 'base', 'pragtech_dental_management', 'cost_center_hierarchy'],
    'website': '',
    'data': [
        'data/state_color_data.xml',
        'views/templates.xml',
        'views/calendar_resource_view.xml',
'security/ir.model.access.csv',
    ],
    'qweb': ["static/src/xml/*.xml"],
    # 'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
