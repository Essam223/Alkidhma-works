# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def update_payment(self):
        if self.payment_date:
            if self.payment_date == date.today():
                user = super(AccountPayment, self).update_payment()
                return user
            else:
                if self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu') or \
                        self.env.user.has_group('account.group_account_manager'):
                    user = super(AccountPayment, self).update_payment()
                    return user
                else:
                    raise UserError(_(
                        'You are not allowed to do this. Please contact system administrator !!'))
        else:
            user = super(AccountPayment, self).update_payment()
            return user

    @api.multi
    def delete_payment(self):
        if self.payment_date:
            if self.payment_date == date.today():
                user = super(AccountPayment, self).delete_payment()
                return user
            else:
                if self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu') or \
                        self.env.user.has_group('account.group_account_manager'):
                    user = super(AccountPayment, self).delete_payment()
                    return user
                else:
                    raise UserError(_(
                        'You are not allowed to do this. Please contact system administrator !!'))
        else:
            user = super(AccountPayment, self).delete_payment()
            return user