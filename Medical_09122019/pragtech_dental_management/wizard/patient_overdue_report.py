from odoo import api, fields, models, SUPERUSER_ID
import base64
from odoo.exceptions import Warning


class PatientOverdueReportWizard(models.TransientModel):
    _name = "patient.overdue.report"

    period_start = fields.Date("Period From", required=True, default=fields.Date.context_today)
    period_stop = fields.Date("Period To", required=True, default=fields.Date.context_today)
    patient = fields.Many2one('medical.patient', "Patient")

    @api.multi
    def patient_overdue_report(self):
        patient = False
        if self.patient:
            name = self.patient.name.name
            if self.patient.patient_id:
                name = '[' + self.patient.patient_id + ']' + name
            patient = [self.patient.id, name]
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'patient': patient,
                }
        return self.env.ref('pragtech_dental_management.act_report_patient_overdue').report_action(self, data=data)


class ReportPatientOverdue(models.AbstractModel):

    _name = 'report.pragtech_dental_management.report_patient_overdue'

    @api.model
    def get_pat_overdue_details(self, period_start=False, period_stop=False, patient=False):
        """ Serialise the invoice of the day information

        params: date_start, date_stop string representing the datetime of inv
        """
        dom = [
            ('date_invoice', '>=', period_start),
            ('date_invoice', '<=', period_stop),
            ('type', '=', 'out_invoice'),
            ('is_patient', '=', True),
            ('state', 'in', ('open', 'paid'))
        ]
        if patient:
            dom.append(('patient', '=', patient[0]))
        invoices = self.env['account.invoice'].search(dom)
        invoice_list = []
        for inv in invoices:
            patient_name = False
            if inv.patient:
                nam = inv.patient.name.name
                patient_name = '[' + inv.patient.patient_id + ']' + nam
            order_data = {
                'patient': patient_name,
                'date_invoice': inv.date_invoice,
                'due': inv.residual_signed,
            }
            if inv.residual_signed:
                invoice_list.append(order_data)
        return {
            'orders': sorted(invoice_list, key=lambda l: l['patient'])
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_pat_overdue_details(data['period_start'],
                                          data['period_stop'], data['patient']))
        return data
