# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import date
from odoo.exceptions import ValidationError


class AdvanceDoctor(models.TransientModel):
    _name = "advance.doctor"

    patient_id = fields.Many2one('medical.patient', 'Patient', required=True)
    payment_date = fields.Date('Date', required=True, default=fields.Date.context_today)
    amount = fields.Float('Advance Amount', required=True)

    def action_confirm(self):
        if not self.patient_id.name:
            raise ValidationError(_('Set partner for patient properly !!'))
        domain = [('invoice_journal', '=', True),
                  ('company_id', '=', self.env.user.company_id.id)]
        journal_obj = self.env['account.journal'].search(domain, limit=1)
        payment_methods = journal_obj.inbound_payment_method_ids or journal_obj.outbound_payment_method_ids
        payment_method_id = payment_methods and payment_methods[0] or False
        if payment_method_id:
            payment_method_id = payment_method_id.id

        if journal_obj:
            vals = {'advance': True,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'payment_method_id': payment_method_id,
                    'payment_date': self.payment_date,
                    'journal_id': journal_obj.id,
                    'partner_id': self.patient_id.name.id,
                    'amount': self.amount,
                    'date': date.today()}
            self.env['account.payment'].create(vals)
        else:
            raise ValidationError(_('No journal entry set !!'))
