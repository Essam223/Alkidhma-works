# -*- coding: utf-8 -*-
{
    'name': 'Print Journal Entries',
    'version': '1.0',
    'summary': 'This module allow user to print journal entries in pdf format.',
    'description': """
            """,
    'category': 'Accounting',
    'author': 'Al Kidhma Group',
    'website': '',
    'depends': ['account'],
    'data': ['reports/reports.xml',
             'reports/report_journal_entry.xml',
             'journal_entry_view.xml'
             ],
    'installable': True,
    'application': False,
}
