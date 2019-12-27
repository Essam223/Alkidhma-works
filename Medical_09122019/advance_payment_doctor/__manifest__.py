{
    'name': "Advance Payment for Doctors",
    'version': '0.1',
    'sequence': 2,
    'author': "Al Kidhma Group",
    'category': 'Invoicing',
    'description': 'Allows you to manage advance payment collection',
    'depends': ['advance_payment_option'],
    'data': [
        'security/ir.model.access.csv',
        'views/advance_doctor.xml',
        'views/appointment_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
