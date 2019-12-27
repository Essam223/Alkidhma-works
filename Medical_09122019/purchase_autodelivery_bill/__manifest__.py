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
    'name': 'Purchase Auto-delivery Lot and Bill generation',
    'version': '10.0',
    'category': 'purchase',
    'sequence': 2,
    'summary': 'Manage Purchase Auto-delivery Lot and Bill generation',
    'description': """
Manage Purchase Auto-delivery Lot and Bill generation
    """,
    'author': 'Al Kidhma Group',
    'depends': ['base','purchase', 'product', 'account_cost_center', 'update_invoice_payment'
                , 'delivery', 'stock', 'product_expiry', 'invoice_discount_solution'],
    'data': [
        'views/purchase.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
