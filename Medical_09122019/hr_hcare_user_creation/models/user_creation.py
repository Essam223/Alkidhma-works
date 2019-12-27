from odoo import models, fields, api


class UserCreation(models.TransientModel):
    _inherit = 'user.creation'
    _description = 'User Creation Wizard'

    hr = fields.Boolean('HR')

    @api.multi
    def confirm(self):
        user = super(UserCreation, self).confirm()
        remove_user = [(3, user.id)]
        hr_manager_group = self.env['ir.model.data'].get_object('hr', 'group_hr_manager')
        hr_user_group = self.env['ir.model.data'].get_object('hr', 'group_hr_user')
        hr_holidays_manager_group = self.env['ir.model.data'].get_object('hr_holidays', 'group_hr_holidays_manager')
        hr_holidays_user_group = self.env['ir.model.data'].get_object('hr_holidays', 'group_hr_holidays_user')
        hr_attendance_manager_group = self.env['ir.model.data'].get_object('hr_attendance', 'group_hr_attendance_manager')
        hr_attendance_user_group = self.env['ir.model.data'].get_object('hr_attendance', 'group_hr_attendance_user')
        hr_attendance_group = self.env['ir.model.data'].get_object('hr_attendance', 'group_hr_attendance')
        hr_payroll_manager_group = self.env['ir.model.data'].get_object('hr_payroll', 'group_hr_payroll_manager')
        hr_payroll_user_group = self.env['ir.model.data'].get_object('hr_payroll', 'group_hr_payroll_user')
        if self.hr:
            hr_manager_group.write({'users': [(4, user.id)]})
            hr_user_group.write({'users': [(4, user.id)]})
            hr_holidays_manager_group.write({'users': [(4, user.id)]})
            hr_holidays_user_group.write({'users': [(4, user.id)]})
            hr_attendance_manager_group.write({'users': [(4, user.id)]})
            hr_attendance_user_group.write({'users': [(4, user.id)]})
            hr_attendance_group.write({'users': [(4, user.id)]})
            hr_payroll_manager_group.write({'users': [(4, user.id)]})
            hr_payroll_user_group.write({'users': [(4, user.id)]})
        else:
            hr_manager_group.write({'users': remove_user})
            hr_user_group.write({'users': remove_user})
            hr_holidays_manager_group.write({'users': remove_user})
            hr_holidays_user_group.write({'users': remove_user})
            hr_attendance_manager_group.write({'users': remove_user})
            hr_attendance_user_group.write({'users': remove_user})
            hr_attendance_group.write({'users': remove_user})
            hr_payroll_manager_group.write({'users': remove_user})
            hr_payroll_user_group.write({'users': remove_user})
        return user
