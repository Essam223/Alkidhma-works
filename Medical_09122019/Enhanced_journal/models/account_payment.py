# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2004-2008 PC Solutions (<http://pcsol.be>). All Rights Reserved
from odoo import fields, models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')

    company_id = fields.Many2one('res.company', 'Company', index=True, default=_default_company, store=True, readonly=False)

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            rec['company_id'] = invoice['company_id'][0]
        return rec

    def _compute_journal_domain_and_types(self):
        if self.invoice_ids:
            if len(self.invoice_ids) == 1:
                company_id = self.invoice_ids.company_id.id
                self.company_id = company_id
        journal_type = ['bank', 'cash']
        domain = [('invoice_journal', '=', True), ('company_id', '=', self.company_id.id)]
        if self.currency_id.is_zero(self.amount):
            # In case of payment with 0 amount, allow to select a journal of type 'general' like
            # 'Miscellaneous Operations' and set this journal by default.
            journal_type = ['general', 'bank', 'cash']
            self.payment_difference_handling = 'reconcile'
        else:
            if self.payment_type == 'inbound':
                domain.append(('at_least_one_inbound', '=', True))
            else:
                domain.append(('at_least_one_outbound', '=', True))
        return {'domain': domain, 'journal_types': set(journal_type)}


class AccountabstractPayment(models.AbstractModel):
    _inherit = 'account.abstract.payment'

    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('invoice_journal', '=', True), ('type', 'in', ('bank', 'cash'))])
