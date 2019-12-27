# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
# from odoo.tools import amount_to_text_en
from datetime import datetime, timedelta
from ast import literal_eval


class ChequeMaster(models.Model):
	_name = "cheque.master"
	_description = "Cheque Master Book"

	name = fields.Char(string='Cheque Ref', readonly=True)
	cheque_no = fields.Char(string='Cheque No.', readonly=True)
	bank_name = fields.Many2one('account.bank', string='Bank Name', readonly=True)
	date_issue = fields.Date(string='Printed On', readonly=True)
	cheque_date = fields.Date(string='Cheque Date', readonly=True)
	clear_date = fields.Date(string='Cleared Date', readonly=True)
	hold_date = fields.Date(string='Hold Date', readonly=True)
	return_date = fields.Date(string='Returned Date', readonly=True)
	cancel_date = fields.Date(string='Cancelled Date', readonly=True)
	lost_date = fields.Date(string='Lost Date', readonly=True)
	partner_id = fields.Many2one('res.partner', string="Issue To", readonly=True)
	partner_account_id = fields.Many2one('account.account', string="Partner Account", readonly=True)
	receiver_name = fields.Char(string='Receiver Name')
	designation = fields.Char(string='Receiver Designation')
	phone = fields.Char(string='Receiver Contact No.')
	cheque_date_issue = fields.Date(string='Cheque Issue Date')
	payment_ids = fields.One2many('account.payment', 'cheque_id', string='Payment Lines')
	cheque_ids = fields.One2many('issue.cheque', 'cheque_id', string='Cheque Numbers')
	account_move_ids = fields.Many2many('account.move','cheque_move_rel', 'cheque_id', 'move_id', 'Related Accounting Entries', readonly=True)
	state = fields.Selection([
		('new', 'New'),
		('used', 'Used'),
		('reuse', 'Re-used'),
		('printed', 'Printed'),
		('issued', 'Issued'),
		('hold', 'On Hold'),
		('pending', 'Pending'),
		('cleared', 'Cleared'),
		('returned', 'Returned'),
		('cancelled', 'Cancelled'),
		('lost', 'Lost'),
	], string='Status', readonly=True)
	comment = fields.Text(string="Comment")
	amount = fields.Float('Amount', readonly=True)

	@api.multi
	def lost_cheque(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Lost Cheque',
			'view_mode': 'form',
			'view_type': 'form',
			'res_model': 'lost.cheque',
			'target': 'new',
			'context': 'None'
		}

	@api.multi
	def _check_pending(self):
		today = fields.Date.context_today(self)
		today_date = datetime.strptime(today, '%Y-%m-%d').date()
		cheques = ""
		for record in self.search([('state', 'in', ('issued', 'hold'))]):
			if record.cheque_date < today and record.state == 'issued':
				record.write({'state': 'pending'})

			elif record.state == 'hold'and record.hold_date < today:
				record.write({'state': 'pending'})
		ICPSudo = self.env['ir.config_parameter'].sudo()
		alert_days = literal_eval(ICPSudo.get_param('alert_outbound', default='False'))
		alert_date = today_date + timedelta(days=alert_days)
		alert_cheques = []
		for record in self.search([('state', 'in', ('issued', 'hold'))]):
			if record.cheque_date == str(alert_date) and record.state == 'issued':
				cheques = cheques + record.name + ", "
				alert_cheques.append(record)
			elif record.state == 'hold' and record.hold_date == str(alert_date):
				cheques = cheques + record.name + ", "
				alert_cheques.append(record)



		if cheques != "":
			cheques = cheques[:-2]
			cheques = cheques + "\n"
			ICPSudo = self.env['ir.config_parameter'].sudo()
			email = literal_eval(ICPSudo.get_param('email', default='False'))
			vals = {'state': 'outgoing',
					'subject': 'Outbound Cheques Pending List',
					'body_html': """<div>
										<p>Hello,</p>
										<p>This is a system generated reminder mail. The following outbound cheques are pending.</p>
									</div>
									<blockquote>%s</blockquote>
									<div>Thank You</div>""" % (cheques),
					'email_to': email,
					}
			email_id = self.env['mail.mail'].create(vals)
			email_id.send()

	@api.multi
	def immediate_make_pending(self):
		for record in self.search([]):
			record.make_pending()

	@api.multi
	def make_pending(self):
		today = fields.Date.context_today(self)
		if self.cheque_date < today and self.state == 'issued':
			self.write({'state': 'pending'})
		elif self.state == 'hold'and self.hold_date < today:
			self.write({'state': 'pending'})

	@api.multi
	def print_cheque(self):
		return self.env.ref('cheque_management.report_cheque_payment').report_action(self)

	@api.multi
	def amount_to_text(self, amount):
		# convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
		# convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
		# return convert_amount_in_words
		return self.env.user.currency_id.amount_to_text(amount)

	@api.multi
	def issue_cheque(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Issue Cheque',
			'view_mode': 'form',
			'view_type': 'form',
			'res_model': 'issue.cheque.wizard',
			'target': 'new',
			'context': 'None'
		}

	@api.multi
	def clear_cheque(self):
		view = self.env.ref('cheque_management.wizard_clear_cheque')
		return {
			'type': 'ir.actions.act_window',
			'name': 'Cheque Clearance',
			'view_id': view.id,
			'view_mode': 'form',
			'view_type': 'form',
			'res_model': 'clear.cheque',
			'target': 'new',
			'context': 'None'
		}

	@api.multi
	def hold_cheque(self):
		view = self.env.ref('cheque_management.wizard_clear_cheque3')
		return {
			'type': 'ir.actions.act_window',
			'name': 'Cheque Hold',
			'view_id': view.id,
			'view_mode': 'form',
			'view_type': 'form',
			'res_model': 'clear.cheque',
			'target': 'new',
			'context': 'None'
		}

	@api.multi
	def cancel_cheque(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Cheque Cancellation',
			'view_mode': 'form',
			'view_type': 'form',
			'res_model': 'cancel.cheque',
			'target': 'new',
			'context': 'None'
		}

	@api.multi
	def reuse_cheque(self):
		self.write({'state': 'reuse'})
		print("##################SUCESS")

	@api.multi
	def return_cheque(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Cheque Return',
			'view_mode': 'form',
			'view_type': 'form',
			'res_model': 'return.cheque',
			'target': 'new',
			'context': 'None'
		}
