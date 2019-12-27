from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class PatientFeedbackPopup(models.TransientModel):
    _name = 'patient.feedback.wizard'

    patient_id = fields.Many2one('medical.patient', 'Patient', required=True)
    name = fields.Many2one('medical.physician', 'Attended Doctor')
    language = fields.Selection([('english', 'English'),
                                 ('arabic', 'Arabic')], 'Language', required=True, default='english')
    feedback_date = fields.Date('Date', default=fields.Date.context_today, required=True)
    q1 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '1. Did your Medical provider clearly explain to you the condition of your teeth & gums?')
    q2 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '2. Were all treatment choices explained to you?')
    q3 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '3. Did you understand any instructions that were explained to you?')
    q4 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '4. Were the costs explained to you before the treatment was started?')
    q5 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '5. Did your provider listen to your concerns?')
    q6 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '6. Did your provider act professionally and treat you in a courteous manner?')
    q7 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '7. Did your provider explain how to keep your mouth healthy?')
    q8 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '8. Did your provider readily help you with any pain you may have experienced?')
    q9 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '9. Are you satisfied with the Medical treatment that you received from your provider?')
    q10 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '10. Would you recommend your Medical care provider to your friends and family members?')
    q11 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '11. Was your provider on time for your scheduled appointments?')
    q12 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '12. Were you provided with information about the Medical Care Center policies?')
    q13 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '13. Was the receptionist courteous and helpful?')
    q14 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '14. Was the cashier courteous and helpful?')
    q15 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '15. Did you find the Medical Care Center to be well maintained?')
    q16 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '16. Would you recommend the Medical Care Center to someone else?')
    q17 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '17. Did you have trouble in finding a parking space?')
    comments = fields.Text('Comments')

    @api.multi
    def action_confirm(self):
        feedback_obj = self.env['patient.feedback']
        vals = self.read()[0]
        if self.patient_id:
            vals['patient_id'] = self.patient_id.id
        if self.name:
            vals['name'] = self.name.id
        feedback_obj.create(vals)


class PatientFeedback(models.Model):
    _name = 'patient.feedback'

    name = fields.Many2one('medical.physician', 'Attended Doctor')
    feedback_id = fields.Char("Ref", readonly=True,default=lambda self: _('New'))
    patient_id = fields.Many2one('medical.patient', 'Patient')
    language = fields.Selection([('english', 'English'),
                                 ('arabic', 'Arabic')], 'Language', required=True, default='english')
    feedback_date = fields.Date('Date', default=fields.Date.context_today, required=True)
    q1 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '1. Did your Medical provider clearly explain to you the condition of your teeth & gums?')
    q2 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '2. Were all treatment choices explained to you?')
    q3 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '3. Did you understand any instructions that were explained to you?')
    q4 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '4. Were the costs explained to you before the treatment was started?')
    q5 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '5. Did your provider listen to your concerns?')
    q6 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '6. Did your provider act professionally and treat you in a courteous manner?')
    q7 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '7. Did your provider explain how to keep your mouth healthy?')
    q8 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '8. Did your provider readily help you with any pain you may have experienced?')
    q9 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                          '9. Are you satisfied with the Medical treatment that you received from your provider?')
    q10 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '10. Would you recommend your Medical care provider to your friends and family members?')
    q11 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '11. Was your provider on time for your scheduled appointments?')
    q12 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '12. Were you provided with information about the Medical Care Center policies?')
    q13 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '13. Was the receptionist courteous and helpful?')
    q14 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '14. Was the cashier courteous and helpful?')
    q15 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '15. Did you find the Medical Care Center to be well maintained?')
    q16 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '16. Would you recommend the Medical Care Center to someone else?')
    q17 = fields.Selection([('YES', 'YES'), ('NO', 'NO'), ('not_apply', 'Does Not Apply'), ],
                           '17. Did you have trouble in finding a parking space?')
    comments = fields.Text('Comments')

    @api.model
    def create(self, vals):
        if vals.get('feedback_id', 'New') == 'New':
            vals['feedback_id'] = self.env['ir.sequence'].next_by_code('patient.feedback') or 'New'
        result = super(PatientFeedback, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        raise ValidationError(
            _('You cannot delete feedback record.'))
        return super(PatientFeedback, self).unlink()
