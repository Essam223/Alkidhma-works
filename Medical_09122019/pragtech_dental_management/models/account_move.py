# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def post(self):
        invoice = self._context.get('invoice', False)
        self._post_validate()
        for move in self:
            move.line_ids.create_analytic_lines()
            if move.name == '/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.is_insurance_company:
                    patient_invoice = self.env['account.invoice'].search([('insurance_invoice', '=', invoice.id)],
                                                                         limit=1)
                    new_name = "INS/" + patient_invoice.number.split('/')[1] + '/' + patient_invoice.number.split('/')[
                        2]
                elif invoice and invoice.move_name and invoice.move_name != '/':
                    new_name = invoice.move_name
                else:
                    if journal.sequence_id:
                        # If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
                        sequence = journal.sequence_id
                        if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
                            if not journal.refund_sequence_id:
                                raise UserError(_('Please define a sequence for the credit notes'))
                            sequence = journal.refund_sequence_id
                        if  len(move.date) < 15:
                            new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
                        else:
                            from datetime import datetime
                            date_here = datetime.strptime(move.date, '%Y-%m-%d %H:%M:%S')
                            new_name = sequence.with_context(ir_sequence_date=str(date_here.date())).next_by_id()
                    else:
                        raise UserError(_('Please define a sequence on the journal.'))

                if new_name:
                    move.name = new_name
        return self.write({'state': 'posted'})