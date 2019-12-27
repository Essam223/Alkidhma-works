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
    'name': 'Setting mandatory fields for patient file',
    'version': '11.0',
    'category': 'Generic Modules/Others',
    'sequence': 2,
    'summary': 'Setting mandatory fields for patient file',
    'description': """
Setting mandatory fields for patient file
    """,
    'author': 'Al Kidhma Group',
    'depends': ['pragtech_dental_management', 'calendar_scheduler'],
    'data': [
        'views/appointment.xml',
		'views/calendar.xml',
        'wizard/patient_data_update.xml',
        'templates.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
