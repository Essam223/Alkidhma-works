# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalTeethTreatment(models.Model):
    _inherit = "medical.teeth.treatment"

    patient_id = fields.Many2one('medical.patient', 'Patient Details', readonly=False)
    teeth_id = fields.Many2one('teeth.code', 'Tooth', readonly=False)
    description = fields.Many2one('product.product', 'Description', readonly=False, required=True,
                                  domain=[('is_treatment', '=', True)])
    detail_description = fields.Text('Surface', readonly=False)
    state = fields.Selection(
        [('planned', 'Planned'), ('condition', 'Condition'), ('completed', 'Completed'), ('in_progress', 'In Progress'),
         ('invoiced', 'Invoiced'), ('initial_examination', 'Initial Examination')], 'Status', default='planned',
        readonly=True)
    dentist = fields.Many2one('medical.physician', 'Doctor')
    amount = fields.Float('After Discount', readonly=False)
    actual_amount = fields.Float('Actual Amt', compute='_get_actual_amount', readonly=True)
    appt_id = fields.Many2one('medical.appointment', 'Appointment ID', required=True)
    teeth_code_rel = fields.Many2many('teeth.code', 'teeth_code_medical_teeth_treatment_rel', 'operation', 'teeth')
    diagnosis_id = fields.Many2one('diagnosis', 'Diagnosis')
    diagnosis_description = fields.Text('Notes')
    treatment_invoice = fields.Many2one("treatment.invoice")
    amt_paid_by_patient = fields.Float('Co-payment(%)', default=100, readonly=True, compute='_onchange_amt')
    amt_to_be_patient = fields.Float('Payment by Patient', compute='_onchange_amt')
    tree_control = fields.Boolean('Control')

    @api.onchange('teeth_code_rel')
    def _onchange_tooth(self):
        for rcd in self:
            if rcd.teeth_code_rel:
                count = 0
                multi_tooth = 0
                teeth = False
                surface = ""
                for teeth_code in rcd.teeth_code_rel:
                    if not multi_tooth:
                        if teeth_code.name == 'Upper Jaw':
                            teeth = teeth_code.id
                            multi_tooth = 1
                            surface = 'Upper_Jaw'
                        elif teeth_code.name == 'Lower Jaw':
                            teeth = teeth_code.id
                            multi_tooth = 1
                            surface = 'Lower_Jaw'
                        elif teeth_code.name == 'Full Mouth':
                            teeth = teeth_code.id
                            multi_tooth = 1
                            surface = 'Full_mouth'
                        elif teeth_code.name == 'No Tooth':
                            teeth = teeth_code.id
                            multi_tooth = 1
                            surface = 'No_tooth'
                        else:
                            pass

                if multi_tooth:
                    rcd.teeth_code_rel = [(6, 0, [teeth])]
                else:
                    for i in rcd.teeth_code_rel:
                        count += 1
                        if count == 1:
                            teeth = i.id
                            surface = 'toothcap_' + str(i.name)
                        else:
                            surface = surface + ',toothcap_' + str(i.name)
                rcd.update({'detail_description': surface})
                if count == 1:
                    rcd.teeth_id = teeth
                else:
                    rcd.teeth_id = False
            else:
                rcd.teeth_id = False
                rcd.detail_description = ""

    @api.depends('description')
    def _get_actual_amount(self):
        for appt in self:
            if appt.description:
                appt.update({
                    'actual_amount': appt.description.lst_price,
                    'amount': appt.description.lst_price,
                })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'planned':
                raise ValidationError(_('You can delete only the record with planned status.'))
        return super(MedicalTeethTreatment, self).unlink()

    @api.multi
    def action_go_back(self):
        for result in self:
            invoiced_treatments = self.env['treatment.invoice'].search([('treatment_id', '=', result.id)])
            if invoiced_treatments:
                for i in invoiced_treatments:
                    if result.state == 'in_progress':
                        if i.appointment_id.state in ['done', 'visit_closed']:
                            raise ValidationError(_("You can't do this as the invoice is already generated."
                                                    " Try reopen appointment %s" % i.appointment_id.name))
                        i.unlink()
                        result.inv_status = 'draft'
                        result.state = 'planned'
                    else:
                        result.state = 'in_progress'
            else:
                if result.state == 'in_progress':
                    result.state = 'planned'
                else:
                    result.state = 'in_progress'

    @api.multi
    def action_proceed(self):
        for result in self:
            if result.state == 'planned':
                result.write({'state': 'in_progress'})
            else:
                result.write({'state': 'completed'})
            if result.inv_status != "invoiced":
                invoiced_treatments = self.env['treatment.invoice'].search([('treatment_id', '=', result.id)])
                if invoiced_treatments:
                    pass
                else:
                    if result.patient_id:
                        if result.appt_id.state in ['checkin', 'ready']:
                            result.inv_status = "invoiced"
                            vals = {'appointment_id': result.appt_id.id,
                                    'treatment_id': result.id,
                                    'description': result.description.id,
                                    'note': result.detail_description,
                                    'amount': result.amount,
                                    'actual_amount': result.actual_amount}
                            inv_id = self.env['treatment.invoice'].create(vals)
                        else:
                            dom = [('state', 'in', ['checkin', 'ready']),
                                   ('patient', '=', result.patient_id.id)]
                            app_id = self.env['medical.appointment'].search(dom)
                            appt_id = False
                            if app_id:
                                appt_id = app_id[-1]
                            if appt_id:
                                result.inv_status = "invoiced"
                                result.appt_id = appt_id.id
                                vals = {'appointment_id': appt_id.id,
                                        'treatment_id': result.id,
                                        'description': result.description.id,
                                        'note': result.detail_description,
                                        'amount': result.amount,
                                        'actual_amount': result.actual_amount}
                                inv_id = self.env['treatment.invoice'].create(vals)
            else:
                if result.patient_id and result.appt_id.state not in ['checkin', 'ready']:
                    dom = [('state', 'in', ['checkin', 'ready']),
                           ('patient', '=', result.patient_id.id)]
                    app_id = self.env['medical.appointment'].search(dom)
                    appt_id = False
                    if app_id:
                        appt_id = app_id[-1]
                    if appt_id:
                        result.appt_id = appt_id.id

    @api.model
    def create(self, vals):
        result = super(MedicalTeethTreatment, self).create(vals)
        # if not result.teeth_code_rel:
        #     raise ValidationError(_('Please enter Tooth number properly..'))
        return result

    @api.model
    def write(self, vals):
        result = super(MedicalTeethTreatment, self).write(vals)
        # for i in self:
        #     if not i.teeth_code_rel:
        #         raise ValidationError(_('Please enter Tooth number properly..'))
        return result
