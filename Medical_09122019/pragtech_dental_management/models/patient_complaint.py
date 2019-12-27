# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PatientComplaintWizard(models.Model):
    _name = "patient.complaint.wizard"

    name = fields.Many2one('medical.physician', 'Attended Doctor')
    language = fields.Selection([('english', 'English'),
                                 ('arabic', 'Arabic')], 'Language', required=True, default='english')
    patient_id = fields.Many2one('medical.patient', 'Patient ID')
    complaint_subject = fields.Char('Complaint Subject')
    complaint_date = fields.Date('Date', default=fields.Date.context_today, required=True)
    complaint = fields.Text('Complaint')

    @api.multi
    def action_confirm(self):
        complaint_obj = self.env['patient.complaint']
        vals = self.read()[0]
        if self.patient_id:
            vals['patient_id'] = self.patient_id.id
        if self.name:
            vals['name'] = self.name.id
        complaint_obj.create(vals)


class patient_complaint(models.Model):
    _name = "patient.complaint"

    complaint_id = fields.Char("Ref", readonly=True, default=lambda self: _('New'))
    language = fields.Selection([('english', 'English'),
                                 ('arabic', 'Arabic')], 'Language', readonly=True, required=True, default='english')
    name = fields.Many2one('medical.physician', 'Attended Doctor', readonly=True)
    patient_id = fields.Many2one('medical.patient', 'Patient ID', readonly=True)
    complaint_subject = fields.Char('Complaint Subject', required=True, readonly=True)
    complaint_date = fields.Date('Date', default=fields.Date.context_today, required=True, readonly=True)
    complaint = fields.Text('Complaint', readonly=True)
    action_ta = fields.Text('Action Taken Against')
    action_by = fields.Many2one('res.users', 'Action updated by', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('complaint_id', 'New') == 'New':
            vals['complaint_id'] = self.env['ir.sequence'].next_by_code('patient.complaint') or 'New'
        result = super(patient_complaint, self).create(vals)
        return result

    @api.multi
    def write(self, vals):
        if 'action_ta' in vals:
            vals['action_by'] = self.env.uid
        result = super(patient_complaint, self).write(vals)
        return result

    @api.multi
    def unlink(self):
        raise ValidationError(_('You cannot delete complaint record.'))
        return super(patient_complaint, self).unlink()
