# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class MedicalAppointment(models.Model):
    _inherit = 'medical.appointment'

    session_ids = fields.One2many('medical.session', 'appt_id', 'Sessions')

    @api.multi
    def done(self):
        session_obj = self.env['medical.session']
        for i in self.treatment_ids:
            qty = i.qty
            if qty > 1:
                count = 0
                vals = {
                    'name': i.description.id,
                    'appt_id': i.appointment_id.id,
                    'patient_id': i.patient_id.id,
                    'payline_id': i.id,
                    'state': 'draft'
                }
                while count < qty:
                    session_obj.create(vals)
                    count += 1
        return super(MedicalAppointment, self).done()

    @api.multi
    def action_Reverse(self):
        for i in self.session_ids:
            i.unlink()
        return super(MedicalAppointment, self).action_Reverse()
