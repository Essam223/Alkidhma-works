# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class ConsentForm(models.TransientModel):
    _name = 'consent.form'

    @api.multi
    def get_Consent_for_Final_Cementation(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('Consent for Final Cementation/ '),
            'view_id': self.env.ref('consent_management.view_consent_final_cementation_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'consent.final.cementation',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def get_Cosmetic_treatment_consent(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('INFORMATIONAL INFORMED CONSENT COSMETIC TREATMENT / اقرار بالحصول على المعلومات المتعلقه بالعلاج التجميلي'),
            'view_id': self.env.ref('consent_management.view_cosmetic_treatment_consent_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'cosmetic.treatment.consent',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def get_Endodontic_treatment_Consent(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('Endodontic Treatment Consent Form/ نموذج الموافقة على المعالجة اللبية'),
            'view_id': self.env.ref('consent_management.view_endodontic_treatment_form_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'endodontic.treatment.form',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def get_general_Consent(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('GENERAL CONSENT FOR TREATMENT/ إقرار عام بقبول العلاج'),
            'view_id': self.env.ref('consent_management.view_general_consent_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'general.consent',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }


    @api.multi
    def get_general_dentistry_consent(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('GENERAL CONSENT FORM / استمارة موافقة عامة'),
            'view_id': self.env.ref('consent_management.view_general_dentistry_consent_form_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'general.dentistry.consent',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def get_Oral_Surgery_Consent(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('ORAL SURGERY CONSENT/شهادة جراحة الفم'),
            'view_id': self.env.ref('consent_management.view_oral_surgery_consent_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'oral.surgery.consent',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }


    @api.multi
    def get_Orthodontic_informed_Consent(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('ORTHODONTIC INFORMED CONSENT/ موافقة علمية اعتراضية'),
            'view_id': self.env.ref('consent_management.view_orthodontic_informed_consent_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'orthodontic.informed.consent',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def get_ATTENDANCE(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('ATTENDANCE / الحضور '),
            'view_id': self.env.ref('consent_management.view_attendance_consent_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'attendance.consent',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def get_Refusal_of_Recommended_Treatment(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('REFUSAL OF RECOMMENDED TREATMENT / رفض العلاج الموصى به '),
            'view_id': self.env.ref('consent_management.view_Refusal_of_Recommended_Treatment_wizard').id,
            'type': 'ir.actions.act_window',
            'res_model': 'refusal.of.recommended',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def get_xray_consent(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('X-RAY CONSENT FORM / الموافقة على استخدام الأشعة السينية '),
            'view_id': self.env.ref('consent_management.view_xray_consent_wizard').id,
            'type': 'ir.actions.act_window',
            'res_model': 'xray.consent',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def get_refusal_of_xray(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('INFORMED REFUSAL OF X-RAY CONSENT /اقرار برفض استخدام الأشعة السينية '),
            'view_id': self.env.ref('consent_management.view_refusal_of_xray_consent_wizard').id,
            'type': 'ir.actions.act_window',
            'res_model': 'refusal.of.xray.consent',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def get_photo_release(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('PHOTO AND VIDEO RELEASE FORM /تصريح استخدام الصور الفوتوغرافية والفيديو'),
            'view_id': self.env.ref('consent_management.view_photo_release_wizard').id,
            'type': 'ir.actions.act_window',
            'res_model': 'photo.release',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

