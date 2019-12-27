from odoo import fields, models


class MedicalPhysician(models.Model):
    _inherit = "medical.physician"

    commission_ids = fields.One2many('commission.slab', 'doctor_id', 'Commission details')
