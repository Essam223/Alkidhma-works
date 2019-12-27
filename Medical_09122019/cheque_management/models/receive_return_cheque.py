# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from ast import literal_eval


class ReceiveReturnCheque(models.TransientModel):
    _name = "receive.return.cheque"

    date_return = fields.Date(string='Cheque Return Date', default=fields.Date.context_today, required=True)
    comment = fields.Text(string="Reason Of Return", required=True)

    @api.multi
    def return_cheque(self):
        cheque_obj = self.env['receive.cheque.master'].browse(self.env.context.get('active_id'))
        ICPSudo = self.env['ir.config_parameter'].sudo()
        cheque_journal_r_id = literal_eval(ICPSudo.get_param('cheque_journal_r_id', default='False'))
        if not cheque_journal_r_id:
            raise UserError(_('Set Cheque Receipt Journal under Settings !!!'))
        for i in cheque_obj.payment_ids:
            i.cancel()

        if cheque_obj.comment:
            comment = cheque_obj.comment+ "\n" + self.comment
        else:
            comment = self.comment
        cheque_obj.write({'state': 'returned',
                          'return_to_customer_date': self.date_return,
                          'comment': comment,
                          })
