# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class ConsentForm(models.TransientModel):
    _name = 'consent.form'

    @api.multi
    def get_botox(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('CONSENT FOR BOTOX'),
            'type': 'ir.actions.act_window',
            'res_model': 'consent.botox',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def get_prp(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('CONSENT FORM- Platelet Rich Plasma'),
            'type': 'ir.actions.act_window',
            'res_model': 'consent.prp',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def get_derma_fillers(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('Consent Form for Dema Fillers /نموذج الموافقة على عمل حشوات تجميلية'),
            'type': 'ir.actions.act_window',
            'res_model': 'consent.derma',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def get_chemical_peeling(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('Endodontic Treatment Consent Form/ نموذج الموافقة على المعالجة اللبية'),
            'type': 'ir.actions.act_window',
            'res_model': 'endodontic.treatment.form',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def get_lhr(self):
        contextt = {}
        if self._context.get('patient_id'):
            contextt['default_patient_id'] = self._context['patient_id']
        if self._context.get('doctor_id'):
            contextt['default_doctor_id'] = self._context['doctor_id']
        return {
            'name': _('GENERAL CONSENT FORM / استمارة موافقة عامة'),
            'type': 'ir.actions.act_window',
            'res_model': 'general.dentistry.consent',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }
