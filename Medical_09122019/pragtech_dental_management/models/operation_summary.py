from odoo import api, fields, models, tools, _


class OperationSummary(models.Model):
    _name = "operation.summary"

    @api.model
    def _default_dignose(self):
        st_id = self.env['diagnosis'].search([], limit=1)
        return st_id

    patient_id = fields.Many2one('medical.patient', 'Patient Details')
    teeth_id = fields.Many2one('teeth.code', 'Tooth')
    description = fields.Many2one('product.product', 'Description', domain=[('is_treatment', '=', True)])
    detail_description = fields.Text('Surface')
    state = fields.Selection(
        [('planned', 'Planned'), ('condition', 'Condition'), ('completed', 'Completed'), ('in_progress', 'In Progress'),
         ('invoiced', 'Invoiced'),('initial_examination', 'Initial Examination')], 'Status', default='planned')
    dentist = fields.Many2one('medical.physician', 'Doctor')
    amount = fields.Float('Amount')
    appt_id = fields.Many2one('medical.appointment', 'Appointment ID')
    teeth_code_rel = fields.Many2many('teeth.code', 'teeth_code_medical_teeth_treatment_rel', 'operation', 'teeth')
    diagnosis_id = fields.Many2one('diagnosis', 'Diagnosis', default=_default_dignose)
    diagnosis_description = fields.Text('Notes')
    amt_paid_by_patient = fields.Float('Co-payment(%)', default=100, readonly=True)
    amt_to_be_patient = fields.Float('Payment by Patient', readonly=True)
    # field for checking invoice status
    inv_status = fields.Char(string="Invoice status",
                             store=True,
                             default="draft")





