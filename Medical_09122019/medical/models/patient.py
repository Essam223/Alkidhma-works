# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class MedicalPatient(models.Model):
    _inherit = 'medical.patient'

    @api.multi
    def print_patient_file(self):
        datas = {'doctor': False, 'appointment_sdate': False, 'id_patient': self.id}
        values = self.env.ref('medical.action_report_patient_file').report_action(self.id,
                                                                                             data=datas)
        return values

    @api.multi
    def _patient_age(self):
        def compute_age_from_dates(patient_dob, patient_deceased, patient_dod):
            now = datetime.now()
            if (patient_dob):
                dob = datetime.strptime(patient_dob, '%Y-%m-%d')
                if patient_deceased:
                    dod = datetime.strptime(patient_dod, '%Y-%m-%d %H:%M:%S')
                    delta = relativedelta(dod, dob)
                    deceased = " (deceased)"
                else:
                    delta = relativedelta(now, dob)
                    deceased = ''
                years_months_days = str(delta.years) + "y " + str(delta.months) + "m " + str(
                    delta.days) + "d" + deceased
            else:
                years_months_days = "No DoB !"
            return years_months_days

        for reco in self:
            reco.age = compute_age_from_dates(reco.dob, reco.deceased, reco.dod)