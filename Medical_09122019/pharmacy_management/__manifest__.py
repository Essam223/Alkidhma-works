# -*- coding: utf-8 -*-
{
    'name': 'Pharmacy Management',
    'version': '1.1',
    'category': '',
    'author': 'Al Kidhma Group',
    'website': '',
    'license': 'AGPL-3',
    'depends': ['sale_management', 'sale_stock','purchase', 'product', 'account_cost_center', 'update_invoice_payment'
                , 'delivery', 'stock', 'product_expiry', 'invoice_discount_solution', 'purchase_autodelivery_bill'],
    'data': [
             'security/groups.xml',
             'views/lot_view.xml',
             'views/product.xml',
             'views/sale.xml',
             'views/purchase.xml',
             'views/invoice.xml',
             'wizard/sale_reopen.xml',
             'reports/lot_barcode.xml',
             'reports/report.xml',
             'reports/product_label.xml',
             'reports/report_pharmacy_invoice.xml',
             ],

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [],
}
