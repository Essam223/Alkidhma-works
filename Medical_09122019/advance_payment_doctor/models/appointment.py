# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MedicalAppointment(models.Model):
    _inherit = "medical.appointment"

    @api.multi
    def action_advance(self):
        context = {
            'default_patient_id': self.patient.id
        }
        return {
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('advance_payment_doctor.advance_doctor_wizard').id,
            'res_model': 'advance.doctor',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': context
        }
