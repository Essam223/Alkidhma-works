from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class ArchiveWizard(models.TransientModel):
    _name = 'archive.wizard'

    reason_archive = fields.Text('Reason for Archive', required=True)
    appt_id = fields.Many2one('medical.appointment', 'Appointment', required=True)

    @api.multi
    def action_confirm(self):
        wizard_vals = self.read()[0]
        if wizard_vals['appt_id']:
            appt = self.env['medical.appointment'].browse(wizard_vals['appt_id'][0])
            appt.write({'reason_archive': wizard_vals['reason_archive'],
                        'active': False})