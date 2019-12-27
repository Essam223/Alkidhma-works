from odoo import api, fields, models, tools, _


class TreatmentInvoice(models.Model):
    _inherit = "treatment.invoice"

    # @api.model
    # def create(self, values):
    #     t_inv = super(TreatmentInvoice, self).create(values)
    #     if t_inv.description.type == 'service':
    #         for consumable in t_inv.description.consumable_ids:
    #             vals = {'product_tmpl_id': consumable.product_tmpl_id.id,
    #                    'consu_product_id': consumable.consu_product_id.id,
    #                    'quantity': consumable.quantity,
    #                    'appt_id': t_inv.appointment_id.id,
    #                    'payment_line_id': t_inv.id}
    #             self.env['appt.consumables'].create(vals)
    #     return t_inv
    #
    # @api.multi
    # def write(self, values):
    #     if values.get('description'):
    #         self.env['appt.consumables'].search([('payment_line_id', '=', self.id)]).unlink()
    #         new_description = self.env['product.product'].browse(values.get('description'))
    #         if new_description.type == 'service':
    #             for consumable in new_description.consumable_ids:
    #                 vals = {'product_tmpl_id': consumable.product_tmpl_id.id,
    #                         'consu_product_id': consumable.consu_product_id.id,
    #                         'quantity': consumable.quantity,
    #                         'appt_id': self.appointment_id.id,
    #                         'payment_line_id': self.id}
    #                 self.env['appt.consumables'].create(vals)
    #     result = super(TreatmentInvoice, self).write(values)
    #     return result
    #
    # @api.multi
    # def unlink(self):
    #     # for rec in self:
    #     self.env['appt.consumables'].search([('payment_line_id', '=', self.id)]).unlink()
    #     return super(TreatmentInvoice, self).unlink()
