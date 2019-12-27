from odoo import fields, api, models, SUPERUSER_ID, _
from datetime import date
from odoo.exceptions import UserError, ValidationError, Warning
import base64


class MedicalPhysician(models.Model):
    _inherit = "medical.physician"

    target_amount = fields.Integer()
    commission = fields.Float('Commission(%)')

    @api.constrains('commission')
    def _check_commission(self):
        if self.commission:
            if self.commission > 100:
                raise ValidationError(_('Error ! Commission Percentage should not be greater than 100'))
            if self.commission < 0:
                raise ValidationError(_('Error ! Commission Percentage should not be less than 0'))

    @api.onchange('commission')
    def _onchange_commission(self):
        if self.commission > 100:
            raise UserError(_('Commission Percentage should not be greater than 100'))
        if self.commission < 0:
            raise UserError(_('Commission Percentage should not be less than 0'))

