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
    'name': 'Update Invoice Payment',
    'version': '11.0',
    'category': 'Accounting',
    'sequence': 2,
    'summary': 'Update Invoice Payment',
    'description': """
Update Invoice Payment
    """,
    'author': 'Al Kidhma Group',
    'depends': ['account', 'account_cancel', 'Enhanced_journal', 'invoice_discount_solution'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
        'views/payment.xml',
        'wizard/add_discount.xml',
        'wizard/update_wizard.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
