# -*- coding: utf-8 -*-
{
	'name': "Calendar Scheduler",

	'summary': 'Calendar Scheduler View',

	'description': """ """,

	'author': "CT",
	'website': "",

	'category': 'Uncategorized',
	'version': '11.0.1.2.0',

	'depends': [
		'web',
		'base',
		'pragtech_dental_management',
	],

	'data': [
		'security/ir.model.access.csv',
		'data/state_color_data.xml',
		'views/calendar.xml',
		'views/state_color_view.xml',
		'views/saloon_scheduler.xml'
	],
	'qweb': ['static/src/xml/*.xml'],

	'demo': [],
	'application': True,
	'post_init_hook': 'update_appointment_color',
}
