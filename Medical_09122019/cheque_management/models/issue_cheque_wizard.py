# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class IssueChequeWizard(models.TransientModel):
    _name = "issue.cheque.wizard"

    receiver_name = fields.Char(string='Receiver Name', required=True)
    designation = fields.Char(string='Receiver Designation')
    phone = fields.Char(string='Receiver Contact No.', required=True)
    date_issue = fields.Date(string='Cheque Issue Date', default=fields.Date.context_today, required=True)

    @api.multi
    def issue_cheque(self):
        cheque_obj = self.env['cheque.master'].browse(self.env.context.get('active_id'))
        cheque_obj.write({'state': 'issued',
                          'receiver_name': self.receiver_name,
                          'designation': self.designation,
                          'phone': self.phone,
                          'cheque_date_issue': self.date_issue
                          })
