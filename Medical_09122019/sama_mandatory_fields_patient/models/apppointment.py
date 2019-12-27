# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import time
from datetime import date
from datetime import datetime, timedelta


class Appointment(models.Model):
    _inherit = 'medical.appointment'

    patient_type = fields.Selection([('qat', 'Qatari'), ('reside', 'Resident'), ('vist', 'Visit')],
                                    'Patient Type', required=True, default='qat', track_visibility='onchange')

    def checkin(self):
        if self.patient_state == 'withapt':
            contextt = {}
            contextt['no_patient_name'] = False
            contextt['no_patient_phone'] = False
            contextt['no_qid'] = False
            contextt['no_sex'] = False
            contextt['no_dob'] = False
            contextt['no_nationality_id'] = False
            contextt['no_patient_type'] = False
            need_wizard = False
            if self.patient:
                if not self.patient.patient_name:
                    need_wizard = True
                    contextt['no_patient_name'] = True
                if not self.patient.mobile:
                    need_wizard = True
                    contextt['no_patient_phone'] = True
                if not self.patient.qid:
                    need_wizard = True
                    contextt['no_qid'] = True
                if not self.patient.sex:
                    need_wizard = True
                    contextt['no_sex'] = True
                if not self.patient.dob:
                    need_wizard = True
                    contextt['no_dob'] = True
                if not self.patient.nationality_id:
                    need_wizard = True
                    contextt['no_nationality_id'] = True

            else:
                if not self.patient_name:
                    need_wizard = True
                    contextt['no_patient_name'] = True
                if not self.patient_phone:
                    need_wizard = True
                    contextt['no_patient_phone'] = True
                if not self.qid:
                    need_wizard = True
                    contextt['no_qid'] = True
                if not self.sex:
                    need_wizard = True
                    contextt['no_sex'] = True
                if not self.dob:
                    need_wizard = True
                    contextt['no_dob'] = True
                if not self.nationality_id:
                    need_wizard = True
                    contextt['no_nationality_id'] = True

            if need_wizard:
                contextt['default_appt_id'] = self.id
                return {
                    'name': _('Update Patient Data'),
                    'view_id': self.env.ref('sama_mandatory_fields_patient.view_patient_data_update2').id,
                    'type': 'ir.actions.act_window',
                    'res_model': 'patient.data.update',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': contextt
                }
        return super(Appointment, self).checkin()
