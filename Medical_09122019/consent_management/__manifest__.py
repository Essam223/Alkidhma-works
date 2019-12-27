# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: AMEERA.P.P
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
    'name': 'Consent Management',
    'version': '10.0',
    'category': 'Generic Modules/Others',
    'sequence': 2,
    'summary': 'Consent Management',
    'description': """
Consent Management
    """,
    'author': 'Al Kidhma Group',
    'depends': ['web', 'base', 'pragtech_dental_management', 'web_digital_sign'],
    'data': [
        'wizard/general_consent.xml',
        'wizard/orthodontic_informed_consent.xml',
        'wizard/cosmetic_treatment_consent.xml',
        'wizard/attendance.xml',
        'wizard/endodontic_treatment.xml',
        'wizard/Consent_for_Final_Cementation.xml',
        'wizard/general_dentistry_consent.xml',
        'wizard/oral_surgery_consent.xml',
        'wizard/refusal_of_recommended_treatment.xml',
        'wizard/xray_consent.xml',
        'wizard/refusal_of_xray_consent.xml',
        'wizard/photo_release_form.xml',
        'views/consent_form.xml',
        'views/dashboard.xml',
        'reports/report_general_consent_pdf.xml',
        'reports/report_orthodontic_consent_pdf.xml',
        'reports/report_cosmetic_treatment_pdf.xml',
        'reports/report_attendance_pdf.xml',
        'reports/report_endodontic_treatment_pdf.xml',
        'reports/report_final_cementation.xml',
        'reports/report_general_dentistry_consent_pdf.xml',
        'reports/report_oral_surgery_consent_pdf.xml',
        'reports/report_refusal_of_recommended_pdf.xml',
        'reports/report_xray_consent_pdf.xml',
        'reports/report_refusal_of_xray_consent_pdf.xml',
        'reports/report_photo_release.xml',
        'views/appointment.xml',
        'reports/reports.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
