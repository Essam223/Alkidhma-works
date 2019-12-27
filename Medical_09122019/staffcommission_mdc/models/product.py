from odoo import fields, api, models, _
from odoo.exceptions import UserError, ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    overhead_cost = fields.Float('Overhead cost(%)')

    @api.constrains('overhead_cost')
    def _check_overhead_cost(self):
        if self.overhead_cost:
            if self.overhead_cost > 100:
                raise ValidationError(_('Error ! Overhead cost Percentage should not be greater than 100'))
            if self.overhead_cost < 0:
                raise ValidationError(_('Error ! Overhead cost Percentage should not be less than 0'))

    @api.onchange('overhead_cost')
    def _onchange_overhead_cost(self):
        if self.overhead_cost > 100:
            raise UserError(_('Overhead cost Percentage should not be greater than 100'))
        if self.overhead_cost < 0:
            raise UserError(_('Overhead cost Percentage should not be less than 0'))
