from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = "res.users"

    room_ids = fields.Many2many('medical.hospital.oprating.room', 'user_room_rel',
                                'room_id', 'user_id', "Allowed Room Columns")
    physician_ids = fields.Many2many('medical.physician', 'physician_room_rel',
                                     'physician_id', 'user_id', "Allowed Doctor Columns")
