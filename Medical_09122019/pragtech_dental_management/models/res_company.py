from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    patient_prefix = fields.Char("Patient ID Prefix", required=False, default=lambda self: _('PAC'))
    fax = fields.Char("Fax")

    def update_partner_receiv_payable(self, company_id, values_partner):
        company_browse = self.env['res.company'].browse(company_id)
        receiv_val_ref, payable_val_ref = company_browse.get_account_receiv_payable(company_id)
        AccountObj = self.env['account.account']
        if receiv_val_ref:
            values_partner['property_account_receivable_id'] = AccountObj.browse(int(receiv_val_ref)).id
        if payable_val_ref:
            values_partner['property_account_payable_id'] = AccountObj.browse(int(payable_val_ref)).id
        values_partner['company_id'] = company_id
        return values_partner

    def get_account_receiv_payable(self, company_here):
        receiv_val_ref = False
        payable_val_ref = False
        PropertyObj = self.env['ir.property']
        property_account_receivable_id = PropertyObj.search([('name', '=', 'property_account_receivable_id'),
                                                             ('company_id', '=', company_here),
                                                             ('res_id', '=', None),
                                                             ], limit=1)
        if property_account_receivable_id:
            receiv_val_ref = property_account_receivable_id.value_reference.split(',')[1]
        property_account_payable_id = PropertyObj.search([('name', '=', 'property_account_payable_id'),
                                                          ('company_id', '=', company_here),
                                                          ('res_id', '=', None),
                                                          ], limit=1)
        if property_account_payable_id:
            payable_val_ref = property_account_payable_id.value_reference.split(',')[1]
        return receiv_val_ref, payable_val_ref

