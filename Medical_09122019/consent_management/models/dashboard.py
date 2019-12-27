from odoo import api, models, fields, _


class MedicalDashboard(models.Model):
    _inherit = "medical.dashboard"

    @api.multi
    def get_Consent_form(self):
        return {
            'name': _('Consent form'),
            'view_id': self.env.ref('consent_management.view_consent_form_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'consent.form',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }