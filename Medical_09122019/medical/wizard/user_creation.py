from odoo import models, fields, api


class UserCreation(models.TransientModel):
    _inherit = 'user.creation'
    _description = 'User Creation Wizard'

    nurse = fields.Boolean('Nurse')

    @api.multi
    def confirm(self):
        user = super(UserCreation, self).confirm()
        if self.nurse:
            group_nurse = self.env['ir.model.data'].get_object('medical', 'group_dental_nurse_menu')
            group_nurse.write({'users': [(4, user.id)]})
            nurse_obj = self.env['medical.nurse']
            nurse_obj.create({'nurse': user.id})
        return user
