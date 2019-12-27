# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class DateWizard(models.TransientModel):
    _name = 'session.date'

    date = fields.Date('Done On', required=True, default=fields.Date.context_today)

    def confirm(self):
        act_id = self.env.context.get('active_ids', [])
        session_obj = self.env['medical.session'].search([('id', 'in', act_id)])
        session_obj.write({'date': self.date, 'state': 'done'})


class SessionsManagement(models.Model):
    _name = 'medical.session'

    name = fields.Many2one('product.product', 'Treatment')
    date = fields.Date('Date')
    patient_id = fields.Many2one('medical.patient', 'Patient', required=True)
    appt_id = fields.Many2one('medical.appointment', 'Appointment')
    payline_id = fields.Many2one('treatment.invoice', 'Payment Line')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', index=True, readonly=True,
                             copy=False, default='draft')

    @api.multi
    def done(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mark session as Done',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'session.date',
            'target': 'new',
            'context': 'None'
        }

    @api.multi
    def undone(self):
        for i in self:
            i.write({'date': False, 'state': 'draft'})


