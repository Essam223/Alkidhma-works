# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import base64


class MedicalTeethTreatment(models.Model):
    _description = "Teeth Treatment"
    _name = "medical.teeth.treatment"
    _order = "create_date desc"

    patient_id = fields.Many2one('medical.patient', 'Patient Details', readonly=True)
    teeth_id = fields.Many2one('teeth.code', 'Tooth', readonly=True)
    description = fields.Many2one('product.product', 'Description', domain=[('is_treatment', '=', True)], readonly=True)
    detail_description = fields.Text('Surface', readonly=True)
    state = fields.Selection(
        [('planned', 'Planned'), ('condition', 'Condition'), ('completed', 'Completed'), ('in_progress', 'In Progress'),
         ('invoiced', 'Invoiced'),('initial_examination', 'Initial Examination')], 'Status', default='planned', readonly=True)
    dentist = fields.Many2one('medical.physician', 'Doctor')
    amount = fields.Float('After Discount', readonly=True)
    actual_amount = fields.Float('Actual Amt', compute='_get_actual_amount', readonly=True)
    appt_id = fields.Many2one('medical.appointment', 'Appointment ID')
    teeth_code_rel = fields.Many2many('teeth.code', 'teeth_code_medical_teeth_treatment_rel', 'operation', 'teeth')
    diagnosis_id = fields.Many2one('diagnosis', 'Diagnosis')
    diagnosis_description = fields.Text('Notes')
    treatment_invoice = fields.Many2one("treatment.invoice")
    amt_paid_by_patient = fields.Float('Co-payment(%)', default=100, readonly=True, compute='_onchange_amt')
    amt_to_be_patient = fields.Float('Payment by Patient', readonly=True, compute='_onchange_amt')
    inv_status = fields.Char(string="Invoice status", store=True, default="draft")
    signature = fields.Binary(string='Signature')
    updated_date = fields.Date('Updated Date')
    wizard_treatment = fields.Char("Treatment", readonly=True)
    wizard_doctor = fields.Char("Doctor", readonly=True)
    initial = fields.Boolean("Initial", default=False)

    def scheduler_update_surface(self):
        surface_lst = []
        for surface in self.search([]):
            if '0' in surface.detail_description:
                splt_surf = []
                for split_surface in surface.detail_description.split(','):
                    teeth = split_surface.split('_')[0]
                    teeth0 = split_surface.split('_')[1]
                    teeth1 = split_surface.split('_')[1]
                    if teeth0 in ['buccal','distal','lingual','mesial','occlusal', 'incisal']:
                        continue
                    if int(teeth0) < 10:
                        teeth1 = teeth0.replace('0', '')
                        splt_surf.append(teeth + '_' + teeth1)
                    else:
                        splt_surf.append(split_surface)
                    surface_lst.append({
                        'id': surface.id,
                        'detail_description': ','.join(splt_surf)
                    })
            else:
                surface_lst.append({
                    'id': surface.id,
                    'detail_description': surface.detail_description
                })

        for sf in surface_lst:
            treatment = self.browse(sf.get('id'))
            treatment.detail_description = sf.get('detail_description', '')
            print(sf.get('id'))
            print(sf.get('detail_description'))

    def _onchange_amt(self):
        for teeth in self:
            teeth.amt_paid_by_patient = 100
            amt_to_be_patient = teeth.amount
            teeth.amt_to_be_patient = amt_to_be_patient

    @api.depends('description')
    def _get_actual_amount(self):
        for appt in self:
            if appt.description:
                appt.update({
                    'actual_amount': appt.description.lst_price
                })

    @api.model
    def write(self, vals):
        appoints = self.mapped('appt_id')
        for apps in appoints:
            order_lines = self.filtered(lambda x: x.appt_id == apps)
            msg = "<b> Updated Medical Teeth Treatment :</b><ul>"
            for line in order_lines:
                if vals.get('description'):
                    msg += "<li>" + _("Description") + ": %s -> %s <br/>" % (
                    line.description.name, self.env['product.product'].browse(vals['description']).name,)
                # if vals.get('diagnosis_id'):
                #     msg += "<li>" + _("Diagnosis") + ": %s -> %s <br/>" % (
                #     line.diagnosis_id.name, self.env['diagnosis'].browse(vals['diagnosis_id']).code,)
                if vals.get('diagnosis_description'):
                    msg += "<li>" + _("Notes") + ": %s -> %s <br/>" % (
                    line.diagnosis_description, vals['diagnosis_description'],)
                if vals.get('teeth_id'):
                    msg += "<li>" + _("Tooth") + ": %s -> %s <br/>" % (
                    line.teeth_id, self.env['teeth.code'].browse(vals['teeth_id']).name,)
                if vals.get('detail_description'):
                    msg += "<li>" + _("Notes") + ": %s -> %s <br/>" % (
                    line.detail_description, vals['detail_description'],)
                if vals.get('state'):
                    msg += "<li>" + _("State") + ": %s -> %s <br/>" % (line.state, vals['state'],)
                if vals.get('state')=='initial_examination':
                    msg += "<li>" + _("Amount") + ": 0 -> 0 <br/>"
                    msg += "<li>" + _("Co-payment(%)") + ": 0 -> 0 <br/>"
                    msg += "<li>" + _("Payment by Patient") + ": 0 -> 0 <br/>" 
                else:
                    if vals.get('amount'):
                        msg += "<li>" + _("Amount") + ": %s -> %s <br/>" % (line.amount, vals['amount'],)
                    if vals.get('amt_paid_by_patient'):
                        msg += "<li>" + _("Co-payment(%)") + ": %s -> %s <br/>" % (
                        line.amt_paid_by_patient, vals['amt_paid_by_patient'],)
                    if vals.get('amt_to_be_patient'):
                        msg += "<li>" + _("Payment by Patient") + ": %s -> %s <br/>" % (
                        line.amt_to_be_patient, vals['amt_to_be_patient'],)
            msg += "</ul>"
            apps.message_post(body=msg)

        result = super(MedicalTeethTreatment, self).write(vals)
        return result

    @api.model
    def create(self, vals):
#         print("\n vals______on create at endddddddddddddd",vals)
        if vals.get('state')=='initial_examination':
            vals['state'] = 'initial_examination'
            vals['amount']=0
            if vals.get('amt_paid_by_patient'):
                vals['amt_paid_by_patient']=0
#             else:
#                 vals.append('amt_paid_by_patient')
#                 vals['amt_paid_by_patient']=0
            if vals.get('amt_to_be_patient'):
                vals['amt_to_be_patient']=0
#             else:
#                 vals.append('amt_to_be_patient')
#                 vals['amt_to_be_patient']=0
        else:
            if 'state' not in list(vals.keys()):
                vals['state'] = 'planned'
            elif 'state' in list(vals.keys()) and not vals['state']:
                vals['state'] = 'planned'
        
        result = super(MedicalTeethTreatment, self).create(vals)
#         print("\n result^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",result)
        op_summary = self.env['operation.summary']
        operation_summary = op_summary.create(vals)
        app_id = self.env['medical.appointment'].search([('patient', '=', result.patient_id.id),
                                                          ('state', 'in', ['checkin', 'ready'])])
        appt_id = False
        if app_id:
            appt_id = app_id[-1]
        if appt_id:
            result.appt_id = appt_id.id
            operation_summary.appt_id = appt_id.id
        # op_ids = op_summary.search([('appt_id', '=', appt_id.id)])
        # if len(op_ids.ids) > 1:
        if result.state in ['in_progress', 'completed'] and result.inv_status != "invoiced":
            invoiced_treatments = self.env['treatment.invoice'].search([('treatment_id', '=', result.id)])
            if invoiced_treatments:
                pass
            else:
                if result.patient_id:
                    if appt_id:
                        result.inv_status = "invoiced"
                        inv_id = self.env['treatment.invoice'].create({'appointment_id': appt_id.id,
                                                                       'treatment_id': result.id,
                                                                       'description': result.description.id,
                                                                       'note': result.detail_description,
                                                                       'amount': result.amount,
                                                                       'actual_amount': result.actual_amount})
        msg = "<b> Created New Operation:</b><ul>"
        if vals.get('description'):
            msg += "<li>" + _("Description") + ": %s<br/>" % (result.description.name)
        if vals.get('diagnosis_id'):
            msg += "<li>" + _("Diagnosis") + ": %s  <br/>" % (result.diagnosis_id.display_name)
        if vals.get('diagnosis_description'):
            msg += "<li>" + _("Notes") + ": %s  <br/>" % (result.diagnosis_description)
        if vals.get('teeth_id'):
            msg += "<li>" + _("Tooth") + ": %s  <br/>" % (result.teeth_id.name)
        if vals.get('state'):
            msg += "<li>" + _("State") + ": %s  <br/>" % (result.state)
        if vals.get('detail_description'):
            msg += "<li>" + _("Surface") + ": %s  <br/>" % (result.detail_description)
        
        if vals.get('state')=='initial_examination':
            msg += "<li>" + _("Amount") + ": 0 <br/>"
            msg += "<li>" + _("Co-payment(%)") + ":  0 <br/>" 
            msg += "<li>" + _("Payment by Patient") + ": 0  <br/>"
        else:
            if vals.get('amount'):
                msg += "<li>" + _("Amount") + ": %s  <br/>" % (result.amount)
            if vals.get('amt_paid_by_patient'):
                msg += "<li>" + _("Co-payment(%)") + ": %s  <br/>" % (result.amt_paid_by_patient)
            if vals.get('amt_to_be_patient'):
                msg += "<li>" + _("Payment by Patient") + ": %s  <br/>" % (result.amt_to_be_patient)
        msg += "</ul>"
        result.appt_id.message_post(body=msg)
        return result

    @api.multi
    def unlink(self):
        for rec in self:
            msg = "<b> Deleted Operation with Values:</b><ul>"
            if rec.description:
                msg += "<li>" + _("Description") + ": %s <br/>" % (rec.description.name,)
            if rec.diagnosis_id:
                msg += "<li>" + _("Diagnosis") + ": %s  <br/>" % (rec.diagnosis_id.display_name,)
            if rec.diagnosis_description:
                msg += "<li>" + _("Notes") + ": %s  <br/>" % (rec.diagnosis_description)
            if rec.teeth_id:
                msg += "<li>" + _("Tooth") + ": %s  <br/>" % (rec.teeth_id.name)
            if rec.state:
                msg += "<li>" + _("State") + ": %s  <br/>" % (rec.state)
            if rec.detail_description:
                msg += "<li>" + _("Surface") + ": %s  <br/>" % (rec.detail_description)
            if rec.amount:
                msg += "<li>" + _("Amount") + ": %s  <br/>" % (rec.amount)
            if rec.amt_paid_by_patient:
                msg += "<li>" + _("Co-payment(%)") + ": %s  <br/>" % (rec.amt_paid_by_patient)
            if rec.amt_to_be_patient:
                msg += "<li>" + _("Payment by Patient") + ": %s  <br/>" % (rec.amt_to_be_patient)
            msg += "</ul>"
            rec.appt_id.message_post(body=msg)
        return super(MedicalTeethTreatment, self).unlink()

    @api.multi
    def action_consent_form(self):
        treat = ""
        doctor = ""
        patient = ""
        if self.patient_id:
            patient = self.patient_id.name.name
        if self.dentist:
            doctor = self.dentist.name.name
        if self.description:
            treat = self.description.name
        if self.detail_description:
            treat = treat + " : " + self.detail_description
        return {
            'name': _('CONSENT FOR OPERATION / PROCEDURE'),
            'type': 'ir.actions.act_window',
            'res_model': 'treatment.sign.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': False,
            'context': {
                'default_treatment': treat,
                'default_doctor': doctor,
                'default_patient': patient,
            }
        }

    @api.multi
    def print_consent(self):
        data = {'ids': self.ids}
        treat = ""
        patient = ""
        if self.patient_id:
            patient = self.patient_id.name_get()[0][1]
        if self.description:
            treat = self.description.name
        if self.detail_description:
            treat = treat + " : " + self.detail_description
        data, data_format = self.env.ref('pragtech_dental_management.report_treatment_sign2_pdf').render(self.ids,
                                                                                                         data=data)
        att_id = self.env['ir.attachment'].create({
            'name': 'Consent_' + treat + "_" + self.updated_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': patient + '_consent.pdf',
            'res_model': 'medical.patient',
            'res_id': self.patient_id.id,
            'mimetype': 'application/pdf'
        })
