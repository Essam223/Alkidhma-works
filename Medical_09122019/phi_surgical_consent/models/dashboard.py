from odoo import api, models, fields, _


class MedicalDashboard(models.Model):
    _inherit = "medical.dashboard"

    @api.multi
    def get_surgical_consent(self):
        contextt = {}
        return {
            'name': _('Surgical consent'),
            'view_id': self.env.ref('phi_surgical_consent.view_surgical_consent_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'surgical.consent',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }
