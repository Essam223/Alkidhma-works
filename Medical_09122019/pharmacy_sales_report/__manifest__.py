# -*- coding: utf-8 -*-

##############################################################################
#
#    Author: Al Kidhma Group
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Pharmacy Sales Report',
    'version': '10.0',
    'category': 'Generic Modules/Others',
    'sequence': 2,
    'summary': 'Manage Reporting',
    'description': """
Pharmacy Sales Reports
    """,
    'author': 'Al Kidhma Group',
    'company': 'Al Kidhma Group',
    'website': 'http://www.alkidhmagroup.com',
    'depends': ['pharmacy_management'],
    'data': [
        'views/sales_report_wizard.xml',
        'views/sales_report.xml',
        'views/report.xml',
        'views/sales_report_cron.xml',
        # 'security/ir.model.access.csv',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
