# -*- coding: utf-8 -*-
{
    'name': 'Consumables for Service Products',
    'version': '1.1',
    'category': 'Accounting',
    'author': 'Al Kidhma Group',
    'website': '',
    'license': 'AGPL-3',
    'depends': ['product', 'pragtech_dental_management'],
    'data': [
             'security/consumable_security.xml',
             'security/ir.model.access.csv',
             'wizard/stock_reversal.xml',
             'views/physician.xml',
             'views/stock_picking.xml',
             'views/product.xml',
             'views/appointment.xml',
             ],

    'demo': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}
