{
    'name': 'Expense Vouchers',
    'version': '11.0.1.0.0',
    'summary': 'Payment and Receipt Vouchers',
    'description': """
        TODO
        
        old description:
        Invoicing & Payments by Accounting Voucher & Receipts
        =====================================================
        The specific and easy-to-use Invoicing system in Odoo allows you to keep track of your accounting, even when you are not an accountant. It provides an easy way to follow up on your vendors and customers. 
        
        You could use this simplified accounting in case you work with an (external) account to keep your books, and you still want to keep track of payments. 
        
        The Invoicing system includes receipts and vouchers (an easy way to keep track of sales and purchases). It also offers you an easy method of registering payments, without having to encode complete abstracts of account.
        
        This module manages:
        
        * Voucher Entry
        * Voucher Receipt
        * Voucher Payment
        \n      
            """,
    'category': 'Accounting',
    'author': 'Al Kidhma Group',
    'website': '',
    'depends': ['base', 'account_invoicing', 'account_cancel', 'account_voucher', 'print_journal_entry'],
    'data': [

        'data/account_voucher_data.xml',
        'views/account_voucher_views.xml',
        'wizard/account_report_general_ledger_view.xml',
        'reports/report_trialbalance.xml',
        'reports/reports.xml',
        'reports/account_voucher_reports.xml',


    ],
    'installable': True,
    'auto_install': False,
}