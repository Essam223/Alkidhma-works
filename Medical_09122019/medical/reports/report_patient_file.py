from odoo import api, fields, models, tools, _


class PatientFileReport(models.AbstractModel):
    _name = 'report.medical.report_patient_file'

    @api.model
    def get_patient_file_details(self, data):
        appt = self.env['medical.appointment'].search([('id', '=', data['ids'][0])])
        record = {}
        record['appt'] = appt.name
        # record['patient'] = appt.patient_name or ''
        record['doctor'] = appt.doctor.name.name
        return record

    @api.multi
    def get_report_values(self, docids, data=None):
        # data = dict(data or {})
        # data.update(self.get_patient_file_details(data))
        # # data.update(self.get_patient_file_details(data['ids'][0]))
        # return data
        appointment_sdate = False
        doctor = False
        docs = False
        if docids:
            docs = self.env['medical.patient'].browse(docids)
        if not docids:
            docs = self.env['medical.patient'].browse(data['id_patient'])
            appointment_sdate = data['appointment_sdate']
            doctor = data['doctor']
        return {
            'doc_ids': self.ids,
            'doc_model': 'medical.patient',
            'data': data,
            'docs': docs,
            'doctor': doctor,
            'appointment_sdate': appointment_sdate,
        }
