from odoo import api, fields, models
from datetime import datetime, timedelta


class DetailedPatientOverdueWizard(models.TransientModel):
    _name = "detailed.patient.overdue.report"

    def _get_start_time(self):
        start_time = datetime.now()
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = start_time - timedelta(hours=3)
        return start_time

    def _get_end_time(self):
        start_time = datetime.now()
        end_time = start_time.replace(hour=20, minute=59, second=59, microsecond=0)
        return end_time

    def _get_doctor_id(self):
        domain = []
        doc_ids = None
        group_dental_doc_menu = self.env.user.has_group('pragtech_dental_management.group_dental_doc_menu')
        group_dental_user_menu = self.env.user.has_group('pragtech_dental_management.group_dental_user_menu')
        group_dental_mng_menu = self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu')
        if group_dental_doc_menu and not group_dental_user_menu and not group_dental_mng_menu:
            partner_ids = [x.id for x in
                           self.env['res.partner'].search(
                               [('user_id', '=', self.env.user.id), ('is_doctor', '=', True)])]
            if partner_ids:
                doc_ids = [x.id for x in self.env['medical.physician'].search([('name', 'in', partner_ids)])]
            domain = [('id', 'in', doc_ids)]
        return domain

    is_only_doctor = fields.Boolean()
    period_start = fields.Datetime("Period From", default=_get_start_time)
    period_stop = fields.Datetime("Period To", default=_get_end_time)
    doctor = fields.Many2one('medical.physician', "Doctor", domain=_get_doctor_id)
    patient = fields.Many2one('medical.patient', "Patient")

    @api.model
    def default_get(self, fields):
        res = super(DetailedPatientOverdueWizard, self).default_get(fields)
        res['is_only_doctor'] = False
        self._get_doctor_id()
        doc_ids = None
        group_dental_doc_menu = self.env.user.has_group('pragtech_dental_management.group_dental_doc_menu')
        group_dental_user_menu = self.env.user.has_group('pragtech_dental_management.group_dental_user_menu')
        group_dental_mng_menu = self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu')
        if group_dental_doc_menu and not group_dental_user_menu and not group_dental_mng_menu:
            res['is_only_doctor'] = True
            partner_ids = [x.id for x in
                           self.env['res.partner'].search(
                               [('user_id', '=', self.env.user.id), ('is_doctor', '=', True)])]
            if partner_ids:
                doc_ids = [x.id for x in self.env['medical.physician'].search([('name', 'in', partner_ids)])]
        if doc_ids:
            res['doctor'] = doc_ids[0]
        return res

    @api.multi
    def detailed_pat_overdue_report(self):
        patient = False
        if self.patient:
            name = self.patient.name.name
            if self.patient.patient_id:
                name = '[' + self.patient.patient_id + ']' + name
            patient = [self.patient.id, name]
        doctor = False
        if self.doctor:
            doctor = [self.doctor.id, self.doctor.name.name]
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'doctor': doctor,
            'patient': patient,
                }
        return self.env.ref('detailed_pat_overdue_report.report_patient_det_overdue_pdf').report_action(self, data=data)


class ReportDetailedPatientOverdue(models.AbstractModel):

    _name = 'report.detailed_pat_overdue_report.report_patient_det_overdue'

    def get_doctor_total(self, invoices, type):
        dr_amount_total_signed = 0.0
        dr_total_paid = 0.0
        dr_total_due = 0.0
        for inv in invoices:
            dr_amount_total_signed += inv.amount_total_signed
            paid = inv.amount_total_signed - inv.residual_signed
            dr_total_paid += paid
            dr_total_due += inv.residual_signed
        if type== 'amount_total_signed':
            return dr_amount_total_signed
        if type== 'amount_paid':
            return dr_total_paid
        if type== 'amount_due':
            return dr_total_due
        return 0.0
    @api.model
    def get_appt_details(self, period_start=False, period_stop=False, doctor=False, patient=False):
        dom = [
            ('type', '=', 'out_invoice'),
            ('is_patient', '=', True),
            ('state', 'in', ('open', 'paid'))]
        if period_start:
            dom.append(('date_invoice', '>=', period_start))
        if period_stop:
            dom.append(('date_invoice', '<=', period_stop))
        if doctor:
            dom.append(('dentist', '=', doctor[0]))
        if patient:
            dom.append(('patient', '=', patient[0]))
        doctors = self.env['medical.physician'].search([])
        doctrs = []
        doctrs_list = []
        invoice = {}
        for i in doctors:
            doctrs.append(i)
            invoice[i] = []
        invoices = self.env['account.invoice'].search(dom, order="date_invoice asc")
        for inv in invoices:
            if inv.residual_signed:
                if inv.dentist:
                    invoice[inv.dentist].append(inv)
        for each in doctrs:
            invoice[each] = invoice.pop(each)
            doctrs_list.append(each)
        period_start_new = ""
        period_stop_new = ""
        if period_start:
            period_start_new = datetime.strptime(period_start, '%Y-%m-%d %H:%M:%S')
        if period_stop:
            period_stop_new = datetime.strptime(period_stop, '%Y-%m-%d %H:%M:%S')
        return {
            'period_start': period_start_new,
            'period_stop': period_stop_new,
            'patient': patient,
            'doctor': doctor,
            'doctors': doctrs_list,
            'invoices': invoice,
            'get_doctor_total': self.get_doctor_total,
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_appt_details(data['period_start'],
                                          data['period_stop'], data['doctor'], data['patient']))
        return data
