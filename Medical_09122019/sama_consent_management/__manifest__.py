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
    'name': 'Sama Consent Management',
    'version': '10.0',
    'category': 'Generic Modules/Others',
    'sequence': 4,
    'summary': 'Consent Management',
    'description': """
Consent Management
    """,
    'author': 'Al Kidhma Group',
    'depends': ['web', 'base', 'pragtech_dental_management', 'web_digital_sign'],
    'data': [
        'wizard/consent_botox.xml',
        'wizard/consent_prp.xml',
        'wizard/consent_derma.xml',

        'views/consent_form.xml',
        'views/dashboard.xml',
        'report/report_botox.xml',
        'report/report_prp.xml',
        'report/report_derma.xml',

        'views/appointment.xml',
        'report/reports.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
