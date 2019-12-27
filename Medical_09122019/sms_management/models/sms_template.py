from odoo import fields, models


class SmsTemplate(models.Model):
    _name = "sms.template"

    name = fields.Char('Name', required=True)
    message = fields.Text('Messages', required=True)
