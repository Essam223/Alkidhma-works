from odoo import models, fields, api


class UserCreation(models.TransientModel):
    _name = 'user.creation'
    _description = 'User Creation Wizard'

    name = fields.Char('Name', required=True)
    user_name = fields.Char('Username', required=True)
    password = fields.Char('Password', required=True)
    admin = fields.Boolean('Admin')
    doctor = fields.Boolean('Doctor')
    reception = fields.Boolean('Reception')
    accountant = fields.Boolean('Accountant')
    inventory = fields.Boolean('Inventory Manager')
    room_ids = fields.Many2many('medical.hospital.oprating.room', 'newuser_room_rel',
                                'room_id', 'user_id', "Allowed Room Columns")
    physician_ids = fields.Many2many('medical.physician', 'newphysician_room_rel',
                                     'physician_id', 'user_id', "Allowed Doctor Columns")

    @api.multi
    def confirm(self):
        user_obj = self.env['res.users']
        user = user_obj.create({'name': self.name,
                                'login': self.user_name,
                                'password': self.password,
                                })
        user.partner_id.email = self.user_name
        if self.admin:
            admin_group = self.env['ir.model.data'].get_object('pragtech_dental_management', 'group_dental_mng_menu')
            patients_group = self.env['ir.model.data'].get_object('pragtech_dental_management',
                                                                  'group_access_patients_menu')
            patients_group.write({'users': [(4, user.id)]})
            admin_group.write({'users': [(4, user.id)]})
        if self.doctor:
            user.partner_id.is_doctor = True
            doctor_group = self.env['ir.model.data'].get_object('pragtech_dental_management', 'group_dental_doc_menu')
            doctor_group.write({'users': [(4, user.id)]})
        if self.reception:
            reception_group = self.env['ir.model.data'].get_object('pragtech_dental_management', 'group_dental_user_menu')
            patients_group = self.env['ir.model.data'].get_object('pragtech_dental_management',
                                                                  'group_access_patients_menu')
            reception_group.write({'users': [(4, user.id)]})
            patients_group.write({'users': [(4, user.id)]})
        if not self.admin and not self.reception:
            user.room_ids = self.room_ids
            user.physician_ids = self.physician_ids
        remove_user = [(3, user.id)]
        purchase_user_group = self.env['ir.model.data'].get_object('purchase', 'group_purchase_user')
        purchase_user_group.write({'users': remove_user})
        purchase_manager_group = self.env['ir.model.data'].get_object('purchase', 'group_purchase_manager')
        purchase_manager_group.write({'users': remove_user})

        stock_user_group = self.env['ir.model.data'].get_object('stock', 'group_stock_user')
        stock_user_group.write({'users': remove_user})
        stock_manager_group = self.env['ir.model.data'].get_object('stock', 'group_stock_manager')
        stock_manager_group.write({'users': remove_user})

        group_website_publisher = self.env['ir.model.data'].get_object('website', 'group_website_publisher')
        group_website_publisher.write({'users': remove_user})
        group_website_designer = self.env['ir.model.data'].get_object('website', 'group_website_designer')
        group_website_designer.write({'users': remove_user})

        account_group = self.env['ir.model.data'].get_object('account', 'group_account_manager')
        if self.accountant:
            account_group.write({'users': [(4, user.id)]})
        else:
            account_group.write({'users': remove_user})
            billing_group = self.env['ir.model.data'].get_object('account', 'group_account_invoice')
            billing_group.write({'users': [(4, user.id)]})

        stock_group = self.env['ir.model.data'].get_object('stock', 'group_stock_manager')
        if self.inventory:
            stock_group.write({'users': [(4, user.id)]})
        else:
            stock_group.write({'users': remove_user})
            stock_user_group = self.env['ir.model.data'].get_object('stock', 'group_stock_user')
            stock_user_group.write({'users': remove_user})

        sales_manager_group = self.env['ir.model.data'].get_object('sales_team', 'group_sale_manager')
        sales_manager_group.write({'users': remove_user})
        sales_all_group = self.env['ir.model.data'].get_object('sales_team', 'group_sale_salesman_all_leads')
        sales_all_group.write({'users': remove_user})
        sales_own_group = self.env['ir.model.data'].get_object('sales_team', 'group_sale_salesman')
        sales_own_group.write({'users': remove_user})
        return user


