# -*- coding: utf-8 -*-
from datetime import date
import base64
from odoo import api, fields, models, _


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    @api.multi
    def attach_consent_botox(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals': wizard_vals}
        data, data_format = self.env.ref('sama_consent_management.report_consent_botox').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'Consent_for_Botox_' + self.name.name + "_" + register_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_Consent_for_Botox.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def attach_consent_prp(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals': wizard_vals}
        data, data_format = self.env.ref('sama_consent_management.report_consent_prp').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'Consent_for_PRP_' + self.name.name + "_" + register_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_Consent_for_PRP.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def attach_consent_derma(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals': wizard_vals}
        data, data_format = self.env.ref('sama_consent_management.report_consent_derma').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'Consent_for_Derma_Fillers_' + self.name.name + "_" + register_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_Consent_for_Derma_Fillers.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })
