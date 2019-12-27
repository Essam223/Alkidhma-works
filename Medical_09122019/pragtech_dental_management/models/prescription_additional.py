from odoo import api, fields, models, tools, _


class PrescriptionAdditionalLine(models.Model):
    _name = "prescription.additional.line"

    additional_id = fields.Many2one('prescription.additional', 'Additional')
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
    ], 'Duration Unit', default='days')
    note = fields.Char('Description')


class PrescriptionAdditional(models.Model):
    _name = "prescription.additional"

    @api.model
    def _get_default_doctor(self):
        doc_ids = None
        partner_ids = [x.id for x in
                       self.env['res.partner'].search([('user_id', '=', self.env.user.id), ('is_doctor', '=', True)])]
        if partner_ids:
            doc_ids = [x.id for x in self.env['medical.physician'].search([('name', 'in', partner_ids)])]
        if doc_ids:
            return doc_ids[0]
        else:
            return False

    name = fields.Char('Ref', readonly=True, default=lambda self: _('New'))
    prescription_date = fields.Datetime('Prescription Date', default=fields.Datetime.now)
    patient_id = fields.Many2one('medical.patient', 'Patient Details', required=True)
    doctor = fields.Many2one('medical.physician', 'Doctor', required=True, default=_get_default_doctor)
    prescription_ids = fields.One2many('prescription.additional.line', 'additional_id', 'Prescription Lines')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('prescription.additional') or 'New'
        result = super(PrescriptionAdditional, self).create(vals)
        return result

    @api.multi
    def print_prescription(self):
        datas = {'ids': self.ids}
        values = self.env.ref('pragtech_dental_management.prescription_additional_report').report_action(self, data=datas)
        return values


class PrescriptionAdditionalReport(models.AbstractModel):
    _name = 'report.pragtech_dental_management.prescription_additional'

    @api.model
    def get_prescription_details(self, ids=False):
        prescription = self.env['prescription.additional'].search([('id', '=', ids)], limit=1)
        record = {}
        record['name'] = prescription.name
        patient = "[" + prescription.patient_id.patient_id + "] : " + prescription.patient_id.patient_name
        record['patient'] = patient
        record['doctor'] = prescription.doctor
        record['speciality'] = prescription.doctor.speciality.name
        record['license_code'] = prescription.doctor.license_code
        record['date'] = prescription.prescription_date
        record['pres_lines'] = []
        prescriptions = []
        for pres in prescription.prescription_ids:
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
        data.update(self.get_prescription_details(data['ids'][0]))
        return data
