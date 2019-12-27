# -*- coding: utf-8 -*-
from datetime import date
import base64
from odoo import api, fields, models, _


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    @api.multi
    def attach_general_consent(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals':wizard_vals}
        data, data_format = self.env.ref('consent_management.report_general_consent').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'General Consent_' + self.name.name + "_" + register_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_general_consent.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def attach_orthodontic_informed_consent(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals': wizard_vals}
        data, data_format = self.env.ref('consent_management.report_orthodontic_informed_consent').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'Orthodontic Informed Consent_' + self.name.name + "_" + register_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_orthodontic_informed_consent.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def attach_Oral_Surgery_Consent(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals': wizard_vals}
        data, data_format = self.env.ref('consent_management.report_oral_surgery_consent').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'Oral Surgery Consent_' + self.name.name + "_" + register_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_oral_surgery_consent.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def attach_cosmetic_treatment_consent(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals': wizard_vals}
        data, data_format = self.env.ref('consent_management.report_cosmetic_treatment').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'Cosmetic Treatment Consent_' + self.name.name + "_" + register_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_cosmetic_treatment_consent.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def attach_attendance(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals': wizard_vals}
        data, data_format = self.env.ref('consent_management.report_attendance_consent').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'Attendance_' + self.name.name + "_" + register_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_Attendance.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def attach_EndodonticTreatmentForm(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals': wizard_vals}
        data, data_format = self.env.ref('consent_management.report_endodontic_treatment').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'Endodontic_Treatment_Form_' + self.name.name + "_" + register_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_Endodontic_Treatment_Form.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def attach_Consent_for_Final_Cementation(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals': wizard_vals}
        data, data_format = self.env.ref('consent_management.report_Consent_for_Final_Cementation').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'Consent_for_Final_Cementation_' + self.name.name + "_" + register_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_Consent_for_Final_Cementation.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def attach_general_dentistry_consent(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals': wizard_vals}
        data, data_format = self.env.ref('consent_management.report_general_dentistry_consent').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'General_Dentistry_Consent_' + self.name.name + "_" + register_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_General_Dentistry_Consent.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def attach_refusal_of_recommended(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals': wizard_vals}
        data, data_format = self.env.ref('consent_management.report_refusal_of_recommended').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'Refusal_of_Treatment_' + self.name.name + "_" + register_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_Refusal_of_Treatment.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def attach_xray_consent(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals': wizard_vals}
        data, data_format = self.env.ref('consent_management.report_xray_consent').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'Xray_Consent_' + self.name.name + "_" + register_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_Xray_Consent.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def attach_refusal_of_xray_consent(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals': wizard_vals}
        data, data_format = self.env.ref('consent_management.report_refusal_of_xray_consent').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'Refusal_Of_Xray_Consent_' + self.name.name + "_" + register_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_Refusal_Of_Xray_Consent.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def attach_photo_release(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals': wizard_vals}
        data, data_format = self.env.ref('consent_management.report_photo_release').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'Photo_Release_Form_' + self.name.name + "_" + register_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_Photo_Release_Form.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })

