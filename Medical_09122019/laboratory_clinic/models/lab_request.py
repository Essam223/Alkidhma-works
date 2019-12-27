# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class LabRequest(models.Model):
    _inherit = 'lab.request'

    READONLY_STATES_Done = {
        'Done': [('readonly', True)],
    }


    lab_id = fields.Many2one('res.partner', 'Laboratory', required=True, readonly=False,
                              states=READONLY_STATES_Done, track_visibility='onchange',
                             # domain=lambda self: [("company_id", "in", self.env.user.company_id.child_ids),
                             #                      ('is_laboratory','=', True)])
                             domain = [('is_laboratory','=', True)])
    invoice_id = fields.Many2one("account.invoice", "Bill entry", readonly=True, track_visibility='onchange')

    def completed_request(self):
        invoice_vals = {}
        invoice_line_vals = []
        inv_id = False
        patient_brw = self.patient_id
        lab_brw = self.lab_id
        vendor_bill_jr_brw = self.env['account.journal'].search([('type', '=', 'purchase'), ('name', '=', 'Vendor Bills'),
                                                     ('company_id', '=', self.company_id.id)])
        cost_center_id = False
        if self.doctor_id:
            if self.doctor_id.department_id:
                if self.doctor_id.department_id:
                    cost_center_id = self.doctor_id.department_id.cost_center_id.id
        for lab_lines in self.lab_request_line_ids:
            each_line = [0, False]
            product_dict = {}
            product_dict['product_id'] = lab_lines.test_id.id
            product_dict['name'] = lab_lines.test_id.name
            product_dict['quantity'] = 1
            product_dict['price_unit'] = lab_lines.sale_price
            acc_obj = self.env['account.account'].search([('name', '=', 'Local Sales'),
                                                          ('user_type_id', '=', 'Income')], limit=1)
            for account_id in vendor_bill_jr_brw:
                product_dict[
                    'account_id'] = account_id.default_debit_account_id.id if account_id.default_debit_account_id else acc_obj.id
            product_dict['cost_center_id'] = cost_center_id
            each_line.append(product_dict)
            invoice_line_vals.append(each_line)
        # Creating invoice dictionary
        invoice_vals['account_id'] = lab_brw.property_account_receivable_id.id
        invoice_vals['company_id'] = self.company_id.id
        invoice_vals['journal_id'] = vendor_bill_jr_brw.id
        invoice_vals['partner_id'] = lab_brw.id
        invoice_vals['type'] = 'in_invoice'
        invoice_vals['journal_type'] = 'purchase'
        invoice_vals['dentist'] = self.doctor_id.id
        # invoice_vals['patient'] = patient_brw.id
        invoice_vals['cost_center_id'] = cost_center_id
        invoice_vals['is_laboratory'] = True
        invoice_vals['appt_id'] = self.appointment_id.id
        invoice_vals['invoice_line_ids'] = invoice_line_vals
        inv_id = self.env['account.invoice'].create(invoice_vals)
        vals = {'state': 'Done'}
        if inv_id:
            vals['invoice_id'] = inv_id.id
        return self.write(vals)