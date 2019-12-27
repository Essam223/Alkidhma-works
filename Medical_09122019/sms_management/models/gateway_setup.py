from odoo import api, fields, models, _
import requests
from odoo.exceptions import UserError


class GateWaySetup(models.Model):
    _name = "gateway.setup"
    _description = "GateWay Setup"

    name = fields.Char(required=True, string='Name')
    gateway_url = fields.Char(required=True, string='GateWay Url')
    parameter = fields.Text(string='Parameters')
    message = fields.Text('Message')
    mobile = fields.Char('Mobile')

    @api.one
    def sms_test_action(self):
        url = eval(self.gateway_url)
        params = eval(self.parameter)
        mobile = self.mobile
        if len(mobile) == 8 or (len(mobile) == 11 and mobile[:3] == '974') and self.message:
            if len(mobile) == 8:
                mobile = '974' + mobile
            params['smsText'] = self.message
            params['recipientPhone'] = self.mobile
            response = requests.get(url, params=params)
            status_code = response.status_code
            value = {
                'model_id': 'gateway_setup',
                'res_id': self.id,
                'mobile': mobile,
                'message': self.message,
                'response': status_code,
                'gateway_id': self.id,
            }
            self.env['sms.track'].create(value)
        else:
            raise UserError(_('Please enter mobile and message !!!'))

    @api.one
    def send_sms(self, mobiles, message, model, res_id):
        url = eval(self.gateway_url)
        params = eval(self.parameter)
        track_obj = self.env['sms.track']
        if message:
            for mobile in mobiles:
                if len(mobile) == 8 or (len(mobile) == 11 and mobile[:3] == '974') and mobile.isdigit():
                    if len(mobile) == 8:
                        mobile = '974' + mobile
                    params['smsText'] = message
                    params['recipientPhone'] = mobile
                    response = requests.get(url, params=params)
                    status_code = response.status_code
                    value = {
                        'model_id': model,
                        'res_id': res_id,
                        'mobile': mobile,
                        'message': message,
                        'response': status_code,
                        'gateway_id': self.id,
                    }
                    track_obj.create(value)
        else:
            raise UserError(_('Please enter message !!!'))
