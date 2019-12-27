# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from ast import literal_eval
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class CardCharges(models.Model):
    _name = "card.charges"

    def _get_bank_id(self):
        bank_id = False
        if not self.env.user.has_group('base.group_multi_company'):
            ICPSudo = self.env['ir.config_parameter'].sudo()
            bank_id = literal_eval(ICPSudo.get_param('default_bank_id', default='False'))
            if not bank_id:
                raise UserError(_('Please define Bank Journal in Accounting Configuration.'))
        else:
            company_id = self.company_id
            if not company_id:
                company_id = self._default_company()
            bank_id = company_id.default_bank_id.id
            if not bank_id:
                raise UserError(_('Please define Bank Journal in Company Configuration.'))
        return bank_id

    def _get_card_id(self):
        card_id = False
        if not self.env.user.has_group('base.group_multi_company'):
            ICPSudo = self.env['ir.config_parameter'].sudo()
            card_id = literal_eval(ICPSudo.get_param('default_card_id', default='False'))
            if not card_id:
                raise UserError(_('Please define Card Journal in Accounting Configuration.'))
        else:
            company_id = self.company_id
            if not company_id:
                company_id = self._default_company()
            card_id = company_id.default_card_id.id
            if not card_id:
                raise UserError(_('Please define Card Journal in Company Configuration.'))
        return card_id

    def _get_line_id(self):
        if self.card_id:
            journal_ids = [self.card_id.id]
        else:
            journal_ids = self.env['account.journal'].search([('type', '=', 'bank')]).ids
        company_id = self.company_id
        if not company_id:
            company_id = self._default_company()
        domain = [('card_reconcile', '=', False), ('journal_id', 'in', journal_ids), ('debit', '>', 0)
                  , ('company_id', '=', company_id.id)]
        return domain

    @api.onchange('move_lines', 'company_id')
    def onchange_move_lines(self):
        return {
            'domain': {'move_lines': self._get_line_id()}
        }

    @api.constrains('bank_id', 'company_id', 'card_id')
    def _check_same_company_phys(self):
        if self.company_id:
            if self.bank_id.company_id:
                if self.company_id.id != self.bank_id.company_id.id:
                    raise ValidationError(_('Error ! Card Charges and Bank should be of same company'))
            if self.card_id.company_id:
                if self.company_id.id != self.card_id.company_id.id:
                    raise ValidationError(_('Error ! Card Charges and Card Journal should be of same company'))

    @api.onchange('company_id', 'bank_id', 'card_id')
    def onchange_company_id(self):
        self.bank_id = self._get_bank_id()
        self.card_id = self._get_card_id()
        return {
            'domain': {'bank_id': self._domain_bank_id(), 'card_id': self._domain_card_id()},
        }

    def _domain_card_id(self):
        domain = [('company_id', '=', self.company_id.id), ('type', '=', 'bank')]
        return domain

    def _domain_bank_id(self):
        domain = [('company_id', '=', self.company_id.id), ('type', '=', 'bank')]
        return domain

    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')

    company_id = fields.Many2one('res.company', 'Company', index=True, default=_default_company)
    name = fields.Char(string='Name', default='Draft', readonly=True)
    payment_date = fields.Date("Date", required=True, default=fields.Date.context_today)
    bank_id = fields.Many2one('account.journal', 'Bank', required=True, default=_get_bank_id, domain=_domain_bank_id)
    card_id = fields.Many2one('account.journal', 'Card Journal', required=True, default=_get_card_id,
                              domain=_domain_card_id)
    card_amount = fields.Float("Card amount", compute='_get_amount')
    service_charge = fields.Float("Service Charge")
    transfer_amount = fields.Float("Amount Transferring to Bank", compute='_get_amount')
    move_lines = fields.Many2many('account.move.line', 'card_move_line_rel', 'card_reconcile_id', 'line_id',
                                  'Card Lines', domain=_get_line_id)
    journal_entry = fields.Many2one('account.move', 'Related Journal Entry', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')

    @api.multi
    def unlink(self):
        for rcd in self:
            if rcd.state != 'draft':
                raise UserError('Cannot delete record(s) which are already posted or cancelled.')
            res = super(CardCharges, rcd).unlink()
            return res

    @api.depends('move_lines', 'service_charge')
    def _get_amount(self):
        for rcd in self:
            card_amount = 0
            for line in rcd.move_lines:
                card_amount += line.debit
            rcd.card_amount = card_amount
            if rcd.service_charge > card_amount:
                rcd.service_charge = 0
                raise UserError('Service Charge must be less than Card amount.')
            rcd.transfer_amount = card_amount - rcd.service_charge

    def post(self):
        if not self.move_lines:
            raise UserError('Please add atleast one card line.')
        name = self.env['ir.sequence'].next_by_code('card.charges')
        self.name = name
        if not self.env.user.has_group('base.group_multi_company'):
            journal_id = self.env.ref('card_charges_management.card_reconcile_journal', False)
            charges_journal_id = self.env.ref('card_charges_management.card_charges_journal', False)
        else:
            card_reconcile_domain = [('company_id', '=', self.company_id.id), ('name', 'ilike', 'Card Reconciliation'), ('type', '=', 'bank')]
            card_charges_domain = [('company_id', '=', self.company_id.id), ('name', 'ilike', 'Card Charges'), ('type', '=', 'bank')]
            journal_id =  self.env['account.journal'].search(card_reconcile_domain)
            charges_journal_id = self.env['account.journal'].search(card_charges_domain)
        line_ids = [
            (0, 0,
             {'journal_id': journal_id.id, 'account_id': self.bank_id.default_credit_account_id.id, 'name': name,
              'amount_currency': 0.0, 'debit': self.transfer_amount, 'card_reconcile': True,
              'company_id': self.company_id.id}),
            (0, 0, {'journal_id': journal_id.id, 'account_id': charges_journal_id.default_debit_account_id.id,
                    'name': '/', 'amount_currency': 0.0, 'debit': self.service_charge, 'partner_id': False,
                    'card_reconcile': True, 'company_id': self.company_id.id}),
            (0, 0, {'journal_id': journal_id.id, 'account_id': self.card_id.default_debit_account_id.id, 'name': '/',
                    'amount_currency': 0.0, 'credit': self.card_amount, 'partner_id': False, 'card_reconcile': True,
                    'company_id': self.company_id.id})
        ]
        vals = {
            'journal_id': journal_id.id,
            'company_id': self.company_id.id,
            'ref': name,
            'date': self.payment_date,
            'line_ids': line_ids,
        }
        account_move = self.env['account.move'].create(vals)
        account_move.post()
        self.journal_entry = account_move.id
        self.state = 'posted'
        for move in self.move_lines:
            move.write({'card_reconcile': True})

    def action_cancel(self):
        if self.journal_entry:
            self.journal_entry.button_cancel()
        for move in self.move_lines:
            move.write({'card_reconcile': False})
        self.state = 'cancel'
