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
    'name': "Pharmacy Stock Report",

    'summary': """
        Stock Report Module""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Al Kidhma Group",
    'company': 'Al Kidhma Group',
    'website': 'http://www.alkidhmagroup.com',
    'depends': ['pharmacy_management'],
    'category': 'Generic Modules/Others',
    'version': '0.1',

    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/report.xml',
        'views/stock_inout_report_wizard.xml',
        'views/stock_inout_report.xml',
        'views/stock_report.xml',
        'views/stock_report_wizard.xml',
    ],


    'installable': True,
    'application': True,
    'auto_install': False,
}
