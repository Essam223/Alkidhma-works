# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MedicalAppointment(models.Model):
    _inherit = "medical.appointment"

    operation_ids = fields.One2many('medical.teeth.treatment', compute='_compute_operations')

    @api.multi
    @api.model
    @api.depends('state')
    def _compute_operations(self):
        oper_obj = self.env['medical.teeth.treatment']
        for rcd in self:
            if rcd.patient and rcd.state in ['checkin', 'ready', 'done', 'visit_closed']:
                oper_ids = oper_obj.search([('patient_id', '=', rcd.patient.id),
                                            ('appt_id', '!=', rcd.id),
                                            ('state', 'in', ['planned', 'in_progress'])])
            else:
                oper_ids = False
            rcd.operation_ids = oper_ids
