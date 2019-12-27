from odoo import api, models, fields, _


class MedicalDashboard(models.Model):
    _inherit = "medical.appointment"

    @api.multi
    def get_consent_forms(self):
        return {
            'name': _('Consent form'),
            'view_id': self.env.ref('sama_consent_management.view_sama_consent_form_wizard').id,
            'type': 'ir.actions.act_window',
            'res_model': 'consent.form',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {'patient_id': self.patient.id, 'doctor_id': self.doctor.id}
        }
