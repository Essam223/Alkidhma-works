# -*- coding: utf-8 -*-
from datetime import date
import base64
from odoo import api, fields, models, _


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    @api.multi
    def attach_surgical_consent(self, register_date, wizard_vals):
        data = {'ids': self.ids, 'wizard_vals': wizard_vals}
        data, data_format = self.env.ref('phi_surgical_consent.report_surgical_consent_consent').render([1], data=data)
        self.env['ir.attachment'].create({
            'name': 'Surgical/Procedure Consent',
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_Surgical_Consent.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'patient_id': self.id,
            'mimetype': 'application/pdf'
        })
