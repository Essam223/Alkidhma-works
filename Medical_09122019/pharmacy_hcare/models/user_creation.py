from odoo import models, fields, api


class UserCreation(models.TransientModel):
    _inherit = 'user.creation'
    _description = 'User Creation Wizard'

    pharmacy = fields.Selection([('user', 'User'),
                                 ('manager', 'Manager')], 'Pharmacy')

    @api.multi
    def confirm(self):
        user = super(UserCreation, self).confirm()
        if self.pharmacy == 'manager':
            group_pharmacy_manager = self.env['ir.model.data'].get_object('pharmacy_management',
                                                                          'group_pharmacy_manager')
            group_pharmacy_manager.write({'users': [(4, user.id)]})
            stock_user_group = self.env['ir.model.data'].get_object('stock', 'group_stock_user')
            stock_user_group.write({'users': [(4, user.id)]})
        if self.pharmacy == 'user':
            group_pharmacy_user = self.env['ir.model.data'].get_object('pharmacy_management', 'group_pharmacy_user')
            group_pharmacy_user.write({'users': [(4, user.id)]})
            stock_user_group = self.env['ir.model.data'].get_object('stock', 'group_stock_user')
            stock_user_group.write({'users': [(4, user.id)]})
        return user