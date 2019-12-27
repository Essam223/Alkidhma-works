from odoo import api, fields, models, tools, _


class PrescriptionLine(models.Model):
    _name = "prescription.line"

    prescription_date = fields.Datetime('Prescription Date', default=fields.Datetime.now)
    patient_id = fields.Many2one('medical.patient', 'Patient Details', required=True)
    appt_id = fields.Many2one('medical.appointment', 'Appointment')
    doctor = fields.Many2one('medical.physician', 'Doctor', required=True)
    medicine_id = fields.Many2one('product.product', 'Medicine', required=True, ondelete="cascade", domain="[('is_medicament', '=', True)]")
    dose = fields.Float('Dose', help="Amount of medication (eg, 250 mg ) each time the patient takes it")
    dose_unit = fields.Many2one('medical.dose.unit', 'Dose Unit', help="Unit of measure for the medication to be taken")
    form = fields.Many2one('medical.drug.form', 'Form', help="Drug form, such as tablet or gel")
    qty = fields.Integer('x', default=1, help="Quantity of units (eg, 2 capsules) of the medicament")
    common_dosage = fields.Many2one('medical.medication.dosage', 'Frequency',
                                    help="Common / standard dosage frequency for this medicament")
    duration = fields.Integer('Duration',
                              help="Time in between doses the patient must wait (ie, for 1 pill each 8 hours, put here 8 and select 'hours' in the unit field")
    duration_period = fields.Selection([
        ('seconds', 'seconds'),
        ('minutes', 'minutes'),
        ('hours', 'hours'),
        ('days', 'days'),
        ('weeks', 'weeks'),
        ('wr', 'when required'),
    ], 'Duration Unit', default='days', )
    note = fields.Char('Description')

    @api.model
    def create(self, values):
        line = super(PrescriptionLine, self).create(values)
        msg = "<b> Created New Prescription Line:</b><ul>"
        if values.get('medicine_id'):
            msg += "<li>" + _("Medicine") + ": %s<br/>" % (line.medicine_id.name)
        if values.get('common_dosage'):
            msg += "<li>" + _("Frequency") + ": %s  <br/>" % (line.common_dosage.name)
        if values.get('duration'):
            msg += "<li>" + _("Duration") + ": %s  <br/>" % (line.duration)
        if values.get('duration_period'):
            msg += "<li>" + _("Duration Unit") + ": %s  <br/>" % (line.duration_period)
        if values.get('note'):
            msg += "<li>" + _("Description") + ": %s  <br/>" % (line.note)
        msg += "</ul>"
        line.appt_id.message_post(body=msg)
        return line

    @api.multi
    def write(self, values):
        appoints = self.mapped('appt_id')
        for apps in appoints:
            order_lines = self.filtered(lambda x: x.appt_id == apps)
            msg = "<b> Updated Prescription Line :</b><ul>"
            for line in order_lines:
                if values.get('medicine_id'):
                    msg += "<li>" + _("Medicine") + ": %s -> %s <br/>" % (
                    line.medicine_id.name, self.env['product.product'].browse(values['medicine_id']).name,)
                if values.get('common_dosage'):
                    msg += "<li>" + _("Frequency") + ": %s -> %s <br/>" % (line.common_dosage.name,
                                                                           self.env['medical.medication.dosage'].browse(
                                                                               values['common_dosage']).name,)
                if values.get('duration'):
                    msg += "<li>" + _("Duration") + ": %s -> %s <br/>" % (line.duration, values['duration'],)
                if values.get('duration_period'):
                    msg += "<li>" + _("Duration Unit") + ": %s -> %s <br/>" % (
                    line.duration_period, values['duration_period'],)
                if values.get('note'):
                    msg += "<li>" + _("Description") + ": %s -> %s <br/>" % (line.note, values['note'],)
            msg += "</ul>"
            apps.message_post(body=msg)
        result = super(PrescriptionLine, self).write(values)
        return result

    @api.multi
    def unlink(self):
        for rec in self:
            msg = "<b> Deleted Prescription Line with Values:</b><ul>"
            if rec.medicine_id:
                msg += "<li>" + _("Medicine") + ": %s <br/>" % (rec.medicine_id.name,)
            if rec.common_dosage:
                msg += "<li>" + _("Frequency") + ": %s  <br/>" % (rec.common_dosage.name,)
            if rec.duration:
                msg += "<li>" + _("Duration") + ": %s  <br/>" % (rec.duration,)
            if rec.duration_period:
                msg += "<li>" + _("Duration Unit") + ": %s  <br/>" % (rec.duration_period,)
            if rec.note:
                msg += "<li>" + _("Description") + ": %s  <br/>" % (rec.note,)
            msg += "</ul>"
            rec.appt_id.message_post(body=msg)
        return super(PrescriptionLine, self).unlink()


class PrescriptionReport(models.AbstractModel):
    _name = 'report.pragtech_dental_management.prescription_report_pdff'

    @api.model
    def get_sale_details(self, ids=False):
        """ Serialise the appt of the day information

        params: date_start, date_stop string representing the datetime of order
        """

        appt = self.env['medical.appointment'].search([('id', '=', ids)])
        record = {}
        patient = "[" + appt.patient.patient_id + "] : " + appt.patient_name
        record['appt'] = appt.name
        record['patient'] = patient
        # record['patient'] = appt.patient_name or ''
        record['doctor'] = appt.doctor
        record['speciality'] = appt.doctor.speciality.name
        record['license_code'] = appt.doctor.license_code
        record['date'] = appt.appointment_sdate[:10]
        prescriptions = []
        for pres in appt.prescription_ids:
            frequency = ""
            if pres.common_dosage:
                frequency = pres.common_dosage.name
            duration = ""
            if pres.duration:
                duration = str(pres.duration)
            if pres.duration_period:
                duration = duration + " " + str(pres.duration_period)
            pres_data = {
                'medicine_id': pres.medicine_id.name,
                'common_dosage': frequency,
                'duration': duration,
                'note': pres.note or "",
            }
            prescriptions.append(pres_data)
        record['pres_lines'] = prescriptions
        return record

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_sale_details(data['ids'][0]))
        return data
