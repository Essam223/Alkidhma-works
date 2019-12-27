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
    'name': 'Staff Commission Report',
    'version': '10.0',
    'category': 'Generic Modules/Others',
    'sequence': 2,
    'summary': 'Manage Reporting',
    'description': """
Staff Commission Reports
    """,
    'author': 'Al Kidhma Group',
    'depends': ['pragtech_dental_management', 'service_consumable', 'hr_payroll'],
    'data': [
        'views/physician.xml',
        'views/product.xml',
        'wizard/cost_profit.xml',
        'wizard/staff_commission.xml',
        'report/report_cost_profit.xml',
        'report/report_staff_commission.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
