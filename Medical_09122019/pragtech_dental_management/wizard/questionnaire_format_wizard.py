from odoo import api, fields, models


class QuestFormatReport(models.AbstractModel):
    _name = 'report.pragtech_dental_management.report_quest_format'

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        docs = self.env['medical.patient'].browse(data['ids'])
        return {
            'doc_ids': self.ids,
            'doc_model': 'medical.patient',
            'data': data,
            'docs': docs,
        }


class OperationSummary(models.TransientModel):
    _name = "questionnaire.format.wizard"

    language = fields.Selection([('english', 'English'),
                                 ('arabic', 'Arabic')], 'Language', required=True, default='english')

    @api.multi
    def action_confirm(self):
        act_id = self.env.context.get('active_ids', [])
        appt = self.env['medical.appointment'].search([('id', 'in', act_id)])
        if appt.patient:
            appt.patient.language = self.language
            values = appt.patient.print_questionnaire_format()
            return values
