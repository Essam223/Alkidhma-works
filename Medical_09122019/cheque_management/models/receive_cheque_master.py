# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
# from odoo.tools import amount_to_text_en
from datetime import datetime, timedelta
from ast import literal_eval


class ReceiveChequeMaster(models.Model):
    _name = "receive.cheque.master"

    name = fields.Char(string='Cheque No.', readonly=True, required=True)
    partner_id = fields.Many2one('res.partner', string="Received From", readonly=True, required=True)
    partner_account_id = fields.Many2one('account.account', string="Partner Account", readonly=True, required=True)
    received_date = fields.Date(string='Received Date', readonly=True, required=True)
    cheque_date = fields.Date(string='Cheque Date', readonly=True, required=True)
    bank_name = fields.Many2one('customer.bank', string='Customer Bank', readonly=True, required=True)
    bank_id = fields.Many2one('account.bank', string='Deposited To', readonly=True)
    clear_date = fields.Date(string='Cleared Date', readonly=True)
    deposit_date = fields.Date(string='Date of Deposit', readonly=True)
    partner_type = fields.Selection([('customer', 'Customer'),
                                     ('supplier', 'Vendor')],
                                    'Partner Type',
                                    default='customer',
                                    required=True)
    account_move_ids = fields.Many2many('account.move', 'cheque_receive_rel', 'name', 'move_id',
                                        'Related Accounting Entries', readonly=True)
    payment_ids = fields.One2many("account.payment", 'receive_cheque_id', string='Payments', readonly=True,
                                   copy=False)
    comment = fields.Text(string="Comment")
    amount = fields.Float('Amount', readonly=True, required=True)
    state = fields.Selection([
        ('received', 'Cheque Received'),
        ('pending', 'Pending for Deposit'),
        ('hold', 'On Hold'),
        ('deposited', 'Deposited to Bank'),
        ('cleared', 'Cleared'),
        ('dishonoured', 'Cheque Dishonoured'),
        ('returned', 'Cheque Return to Customer'),
    ], string='Status', readonly=True)

    hold_date = fields.Date(string='Hold Date', readonly=True)
    present_date = fields.Date(string='Cheque Present Date', readonly=True)
    date_return = fields.Date(string='Cheque Return Date', readonly=True)
    return_to_customer_date = fields.Date(string='Returned to Customer on', readonly=True)

    @api.multi
    def action_view_payment(self):
        payments = self.mapped('payment_ids')
        action = self.env.ref('account.view_account_payment_tree').read()[0]
        if len(payments) > 0:
            action['domain'] = [('id', 'in', payments.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def hold_cheque(self):
        view = self.env.ref('cheque_management.wizard_clear_cheque4')
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
    def deposit_cheque(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Deposit Cheque',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'deposit.cheque',
            'target': 'new',
            'context': 'None'
        }

    @api.multi
    def clear_cheque(self):
        view = self.env.ref('cheque_management.wizard_receive_clear_cheque')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Clear Cheque',
            'view_id': view.id,
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'receive.clear.cheque',
            'target': 'new',
            'context': 'None'
        }

    @api.multi
    def amount_to_text(self, amount):
        # convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        # convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        # return convert_amount_in_words
        return self.env.user.currency_id.amount_to_text(amount)

    @api.multi
    def print_cheque(self):
        return self.env.ref('cheque_management.report_cheque_receipt').report_action(self)

    @api.multi
    def dishonour_cheque(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dishonour Cheque',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'dishonour.cheque',
            'target': 'new',
            'context': 'None'
        }

    @api.multi
    def return_cheque(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cheque Return to Customer',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'receive.return.cheque',
            'target': 'new',
            'context': 'None'
        }

    @api.multi
    def _check_pending(self):
        today = fields.Date.context_today(self)
        today_date = datetime.strptime(today, '%Y-%m-%d').date()
        cheques = ""
        for record in self.search([('state', 'in', ('received', 'hold'))]):
            if record.cheque_date <= today and record.state == 'received':
                record.write({'state': 'pending'})
            elif record.state == 'hold' and record.hold_date <= today:
                record.write({'state': 'pending'})

        ICPSudo = self.env['ir.config_parameter'].sudo()
        alert_days = literal_eval(ICPSudo.get_param('alert_inbound', default='False'))
        alert_date = today_date + timedelta(days=alert_days)
        alert_cheques = []
        for record in self.search([('state', 'in', ('received', 'hold'))]):
            if record.cheque_date == str(alert_date) and record.state == 'received':
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
                    'subject': 'Inbound Cheques Pending List',
                    'body_html': """<div>
                                        <p>Hello,</p>
                                        <p>This is a system generated reminder mail. The following inbound cheques are pending.</p>
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
        if self.cheque_date <= today and self.state == 'received':
            self.write({'state': 'pending'})
        elif self.state == 'hold' and self.hold_date <= today:
            self.write({'state': 'pending'})

