# -*- coding: utf-8 -*-
from odoo import fields, models, api, _,SUPERUSER_ID
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
import pytz


class MedicalAppointment(models.Model):
    _inherit = "medical.appointment"

    def _appointment_reminder(self):
        date_today = fields.Date.today()
        date_today = datetime.strptime(date_today, '%Y-%m-%d')
        date_tomorrow = date_today + relativedelta(days=1)
        tomorrow_end = date_today + relativedelta(days=2)
        appointments = self.env['medical.appointment'].search([('appointment_sdate', '>', str(date_tomorrow)),
                                                               ('appointment_sdate', '<', str(tomorrow_end)),
                                                               ('state', 'in', ('draft', 'confirmed'))])
        reminder = self.env.ref('sms_management.appointment_reminder')
        company_phone = self.env.user.company_id.phone

        gateway_obj = self.env['gateway.setup'].search([], limit=1)
        if gateway_obj:
            url = eval(gateway_obj.gateway_url)
            params = eval(gateway_obj.parameter)
            track_obj = self.env['sms.track']
            for appt in appointments:
                patient_name = ""
                doctor_name = ""
                appointment_sdate = datetime.strptime(appt.appointment_sdate, '%Y-%m-%d %H:%M:%S')
                user = self.env['res.users'].browse(SUPERUSER_ID)
                tz = pytz.timezone(user.partner_id.tz) or pytz.utc
                appointment_sdate = pytz.utc.localize(appointment_sdate).astimezone(tz)
                appointment_sdate = appointment_sdate.strftime('%d/%m/%Y %I:%M %p')
                appt_date = appointment_sdate[:10]
                appt_time = appointment_sdate[11:]
                if appt.doctor:
                    doctor_name = appt.doctor.name.name
                    doctor_name = doctor_name.upper()
                if appt.patient:
                    mobile = appt.patient.mobile
                    patient_name = appt.patient.patient_name
                else:
                    mobile = appt.patient_phone
                    patient_name = appt.patient_name
                patient_name = patient_name.upper()
                message = reminder.message
                message = message.replace('{patient}', patient_name).replace('{doctor}', doctor_name).\
                    replace('{appt_date}', appt_date).replace('{appt_time}', appt_time).\
                    replace('{company_phone}', company_phone)
                if len(mobile) == 8 or (len(mobile) == 11 and mobile[:3] == '974') and mobile.isdigit():
                    if len(mobile) == 8:
                        mobile = '974' + mobile
                    mobile = str(mobile)
                    params['smsText'] = message
                    params['recipientPhone'] = mobile
                    response = requests.get(url, params=params)
                    status_code = response.status_code
                    value = {
                        'model_id': 'medical.appointment',
                        'res_id': appt.id,
                        'mobile': mobile,
                        'message': message,
                        'response': status_code,
                        'gateway_id': gateway_obj.id,
                    }
                    track_obj.create(value)
                else:
                    print ("No mobile number found!!!")
        else:
            print ("Please setup Gateway properly!!!")
