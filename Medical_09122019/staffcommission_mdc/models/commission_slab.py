from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class CommissionSlab(models.Model):
    _name = "commission.slab"

    from_amt = fields.Integer('Range From', required=True)
    to_amt = fields.Integer('Range Till')
    commission = fields.Float('Commission(%)', required=True)
    doctor_id = fields.Many2one('medical.physician', 'Doctor', required=True)

    @api.constrains('commission')
    def _check_commission(self):
        if self.commission:
            if 0 > self.commission or self.commission > 100:
                raise ValidationError(_('Please enter Commission Percentage Properly !!!'))
        if self.from_amt:
            if 0 >= self.from_amt:
                raise ValidationError(_('Please enter Income range Properly !!!'))
