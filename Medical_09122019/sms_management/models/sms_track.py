from odoo import fields, models


class SmsTrack(models.Model):
    _name = "sms.track"
    _rec_name = 'model_id'

    model_id = fields.Char('Model', readonly=True)
    res_id = fields.Integer('Resource', readonly=True)
    mobile = fields.Char('Mobile', readonly=True)
    response = fields.Char('Response', readonly=True)
    message = fields.Text('Messages', readonly=True)
    gateway_id = fields.Many2one('gateway.setup', string='GateWay', readonly=True)
