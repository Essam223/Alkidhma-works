# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from lxml import etree
from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from ast import literal_eval


SEQ_TYPE = {
	'sale': 'voucher.receipt',
	'purchase': 'voucher.payment',
}


class AccountVoucher(models.Model):
	_inherit = 'account.voucher'


	is_cheque = fields.Boolean('Is Cheque?', default=False)
	# cheque_name = fields.Char(string='Cheque No.')
	cheque_date = fields.Date(string='Cheque Date', default=fields.Date.context_today)
	issued_partner = fields.Many2one('res.partner', string='Issued to')
	cheque_id = fields.Many2one('cheque.master', string='Cheque Number', domain="[('state', '=', 'new')]")
	date_issue = fields.Date(string='Print Date', default=fields.Date.context_today)
	name_in_cheque = fields.Char(string="Name in Cheque")




	@api.onchange('cheque_id')
	def onchange_cheque_id(self):
		ICPSudo = self.env['ir.config_parameter'].sudo()
		cheque_journal_p_id = literal_eval(ICPSudo.get_param('cheque_journal_p_id', default='False'))
		if self.is_cheque:
			self.journal_id = cheque_journal_p_id

		
	@api.onchange('issued_partner')
	def onchange_issued_partner(self):
		if self.is_cheque:
			self.partner_id = self.issued_partner.id
			self.account_id = self.partner_id.property_account_payable_id.id




	@api.multi
	def action_move_line_create(self):
		res = super(AccountVoucher, self).action_move_line_create()
		if self.is_cheque:
			cheque_issue_obj = self.env['issue.cheque']
			cheque_issue_obj.create({
								'cheque_id':self.cheque_id.id,
								'partner_id':self.issued_partner.id,
								'name_in_cheque':self.name_in_cheque,
								'dest_account_id':self.line_ids.account_id.id,
								'amount':self.line_ids.price_subtotal,
								# 'payment_date': self.date_issue,
								'date_issue':self.date_issue,
								'cheque_date':self.cheque_date
								})
			cheque_issue_obj.search(
                    [('cheque_id', '=', self.cheque_id.id)]).post_cheque()

			self.number = self.cheque_id.name

		return res