# -*- coding: utf-8 -*-

##############################################################################
#
#    Author: CYRIL TOMY
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
    'name': 'Sessions Management',
    'version': '10.0',
    'category': 'Generic Modules/Others',
    'sequence': 2,
    'summary': 'Manage sessions',
    'description': """
Sales Reports
    """,
    'author': 'Al Kidhma Group',
    'depends': ['pragtech_dental_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/session_done_wizard.xml',
        'views/treatment_invoice.xml',
        'views/patient.xml',
        'views/appointment.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
