from odoo import api, fields, models, tools, _


class TreatmentInvoice(models.Model):
    _inherit = "treatment.invoice"

    def set_access_for_actual_amount(self):
        for rec in self:
            if  self.env['res.users'].has_group('pragtech_dental_management.group_dental_mng_menu'):
                rec.able_to_modify_actual_amount = True

    able_to_modify_actual_amount = fields.Boolean(compute=set_access_for_actual_amount, string='Is user able to modify Actual Amt?')

    def _get_actual_amount(self):
        for appt in self:
            if appt.description:
                appt.update({
                    'actual_amount': appt.description.lst_price
                })

    actual_amount = fields.Float('Actual Amt', store=True, compute=False)
    # actual_amount = fields.Float('Actual Amt', store=True)

    @api.onchange('treatment_id')
    def onchange_treatment_id(self):
        self.set_access_for_after_discount()
        self.set_access_for_actual_amount()
        if self.treatment_id:
            self.description = self.treatment_id.description

    @api.onchange('description')
    def onchange_description(self):
        if self.description:
            self.actual_amount = self.description.lst_price
            self.amount = self.description.lst_price

    @api.onchange('actual_amount')
    def onchange_actual_amount(self):
        if self.actual_amount:
            self.amount = self.actual_amount