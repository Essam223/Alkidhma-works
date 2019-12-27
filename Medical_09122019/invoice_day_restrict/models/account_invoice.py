# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def modify_invoice(self):
        if self.date_invoice:
            if self.date_invoice == date.today():
                user = super(AccountInvoice, self).modify_invoice()
                return user
            else:
                if self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu') or \
                        self.env.user.has_group('account.group_account_manager'):
                    user = super(AccountInvoice, self).modify_invoice()
                    return user
                else:
                    raise UserError(_(
                        'You are not allowed to do this. Please contact system administrator !!'))
        else:
            user = super(AccountInvoice, self).modify_invoice()
            return user