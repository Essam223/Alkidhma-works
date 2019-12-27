# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class IrAttachment(models.Model):
    """
    Form for Attachment details
    """
    _inherit = "ir.attachment"
    _name = "ir.attachment"

    patient_id = fields.Many2one('medical.patient', 'Patient')
    appointment_id = fields.Many2one('medical.appointment', 'Appointment')

    @api.model
    def create(self, values):
        line = super(IrAttachment, self).create(values)
        msg = "<b> Created New Attachment:</b><ul>"
        if values.get('name'):
            msg += "<li>" + _("Name") + ": %s<br/>" % (line.name)
        msg += "</ul>"
        line.appointment_id.message_post(body=msg)
        return line

    @api.multi
    def write(self, values):
        appoints = self.mapped('appointment_id')
        for apps in appoints:
            order_lines = self.filtered(lambda x: x.appointment_id == apps)
            for line in order_lines:
                msg = "<b> Updated Attachment : </b><ul>"
                if values.get('name'):
                    msg += "<li>" + _("Name") + ": %s -> %s <br/>" % (line.name, values['name'],)
                if not values.get('name'):
                    msg = "<b> Updated File Content of Attachment : %s </b><ul>" % (line.name,)
                msg += "</ul>"
            apps.message_post(body=msg)
        result = super(IrAttachment, self).write(values)
        return result

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.res_model in ['medical.appointment', 'medical.patient']:
                raise ValidationError(_('You cannot delete Attachments.'))
            msg = "<b> Deleted Attachment with Values:</b><ul>"
            if rec.name:
                msg += "<li>" + _("Name") + ": %s <br/>" % (rec.name,)
            msg += "</ul>"
            rec.appointment_id.message_post(body=msg)
        return super(IrAttachment, self).unlink()
