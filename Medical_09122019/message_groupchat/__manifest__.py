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
    'name': 'Group chat and Messaging',
    'version': '11.0',
    'category': 'Medical',
    'sequence': 2,
    'summary': 'Group chat and Messaging',
    'description': """
    Group chat and Messaging
    """,
    'author': 'Al Kidhma Group',
    'depends': ['mail'],
    'data': [
        'views/menu.xml',
        # 'views/templates.xml',
            ],
     'qweb': [
        "static/src/xml/*.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
