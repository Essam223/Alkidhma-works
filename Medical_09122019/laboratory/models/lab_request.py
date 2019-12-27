# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class LabRequest(models.Model):
    _name = 'lab.request'

    READONLY_STATES_Done = {
        'Done': [('readonly', True)],
    }

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lab.request') or 'New'
        result = super(LabRequest, self).create(vals)
        return result

    name = fields.Char('Name', readonly=True, default='New')
    appointment_id = fields.Many2one('medical.appointment', string='Appointment', required=True, readonly=False,
                              states=READONLY_STATES_Done, track_visibility='onchange')
    doctor_id = fields.Many2one('medical.physician', string='Doctor', required=True, readonly=False,
                              states=READONLY_STATES_Done, track_visibility='onchange')
    patient_id = fields.Many2one('medical.patient', 'Patient', required=True, readonly=False,
                              states=READONLY_STATES_Done, track_visibility='onchange')
    lab_date = fields.Datetime('Date', required=True, default=fields.Datetime.now, readonly=False,
                              states=READONLY_STATES_Done, track_visibility='onchange')
    lab_request_line_ids = fields.One2many('lab.request.lines', 'lab_request_id', string='Tests', readonly=False,
                              states=READONLY_STATES_Done, track_visibility='onchange')
    state = fields.Selection([('Draft', 'Draft'), ('Requested', 'Requested'), ('Accepted', 'Accepted'),
                              ('In_Progress', 'In Progress'), ('Done', 'Done'), ('Cancel', 'Cancel')],
                             'State', default='Draft', track_visibility='onchange')
    user_id = fields.Many2one('res.users', 'Lab User', readonly=False,
                              states=READONLY_STATES_Done, track_visibility='onchange')
    invoice_id = fields.Many2one("account.invoice", "Invoice entry", readonly=True, track_visibility='onchange')
    attach_count = fields.Integer(string='# of Attachments', compute='_get_attached', readonly=True)
    attachment_ids = fields.One2many('ir.attachment', 'lab_request_id', 'Attach Results', track_visibility='onchange')

    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')

    company_id = fields.Many2one('res.company', 'Company', index=True, default=_default_company, readonly=False,
                              states=READONLY_STATES_Done, track_visibility='onchange')

    @api.depends('attachment_ids')
    def _get_attached(self):
        for appt in self:
            if appt.attachment_ids:
                attach_count = len(appt.attachment_ids)
                appt.update({
                    'attach_count': attach_count,
                })
            else:
                appt.update({
                    'attach_count': 0,
                })

    @api.multi
    def show_attachments(self):
        attachments = self.mapped('attachment_ids')
        action = self.env.ref('pragtech_dental_management.action_attachments').read()[0]
        if len(attachments) > 0:
            action['domain'] = [('id', 'in', attachments.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def submit_request(self):
        self.state = 'Requested'

    def accept_request(self):
        self.state = 'Accepted'

    def in_progress_request(self):
        self.state = 'In_Progress'

    def completed_request(self):
        invoice_vals = {}
        invoice_line_vals = []
        inv_id = False
        patient_brw = self.patient_id
        partner_brw = patient_brw.name
        jr_brw = self.env['account.journal'].search([('type', '=', 'sale'), ('name', '=', 'Customer Invoices'), ('company_id', '=', self.company_id.id)])
        cost_center_id = False
        if self.doctor_id:
            if self.doctor_id.department_id:
                if self.doctor_id.department_id:
                    cost_center_id = self.doctor_id.department_id.cost_center_id.id
        for lab_lines in self.lab_request_line_ids:
            each_line = [0, False]
            product_dict = {}
            product_dict['product_id'] = lab_lines.test_id.id
            p_brw = lab_lines.test_id
            if self.appointment_id.insurance_id.company_id.id in [comp.id for comp in
                                                               p_brw.insurance_company_ids]:
                product_dict[
                    'amt_paid_by_patient'] = self.appointment_id.insurance_id.company_id.amt_paid_by_patient
                product_dict['discount_amt'] = self.appointment_id.insurance_id.company_id.discount_amt
            product_dict['name'] = lab_lines.test_id.name
            product_dict['quantity'] = 1
            product_dict['price_unit'] = lab_lines.sale_price
            acc_obj = self.env['account.account'].search([('name', '=', 'Local Sales'),
                                                          ('user_type_id', '=', 'Income')], limit=1)
            for account_id in jr_brw:
                product_dict[
                    'account_id'] = account_id.default_debit_account_id.id if account_id.default_debit_account_id else acc_obj.id
            product_dict['cost_center_id'] = cost_center_id
            each_line.append(product_dict)
            invoice_line_vals.append(each_line)
        # Creating invoice dictionary
        invoice_vals['account_id'] = partner_brw.property_account_receivable_id.id
        invoice_vals['company_id'] = self.company_id.id
        invoice_vals['journal_id'] = jr_brw.id
        invoice_vals['partner_id'] = partner_brw.id
        invoice_vals['dentist'] = self.doctor_id.id
        invoice_vals['cost_center_id'] = cost_center_id
        invoice_vals['is_patient'] = True
        invoice_vals['appt_id'] = self.appointment_id.id
        invoice_vals['insurance_company'] = self.appointment_id.insurance_id.company_id.id
        invoice_vals['invoice_line_ids'] = invoice_line_vals
        inv_id = self.env['account.invoice'].create(invoice_vals)
        vals = {'state': 'Done'}
        if inv_id:
            vals['invoice_id'] = inv_id.id
        return self.write(vals)

    def cancel_request(self):
        self.state = 'Cancel'

    @api.multi
    def print_report(self):
        return self.env.ref('laboratory.action_report_lab_order').report_action(self)


class LabRequestLines(models.Model):
    _name = 'lab.request.lines'

    lab_request_id = fields.Many2one('lab.request', string='Lab Order', required=True)
    Special_Instructions = fields.Char('Special Instructions')
    test_id = fields.Many2one('product.product', string='Test', required=True, help='Insurance company plan')
    sale_price = fields.Float('Sale Price')

    @api.onchange('test_id')
    def onchange_test_id(self):
        if self.test_id:
            self.sale_price = self.test_id.list_price


class MedicalAppointment(models.Model):
    _inherit = 'medical.appointment'

    lab_ids = fields.One2many('lab.request', 'appointment_id', string='Lab Orders')

    @api.multi
    def action_view_lab_request(self):
        lab_requests = self.mapped('lab_ids')
        action = self.env.ref('laboratory.action_lab_request').read()[0]
        if len(lab_requests) > 1:
            action['domain'] = [('id', 'in', lab_requests.ids)]
        elif len(lab_requests) == 1:
            action['views'] = [(self.env.ref('laboratory.lab_request_form').id, 'form')]
            action['res_id'] = lab_requests.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def _get_lab_request(self):
        for appointment in self:
            lab_ids = self.env['lab.request'].search([('appointment_id', '=', appointment.id)])
            appointment.update({
                'lab_request_count': len(set(lab_ids.ids)),
                'lab_ids': lab_ids.ids,
            })

    lab_request_count = fields.Integer(string='# of Lab Orders', compute='_get_lab_request', readonly=True)

    @api.multi
    def lab_request(self):
        return {
            'name': _('Lab Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'lab.request',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': False,
            'context': {
                'default_appointment_id': self.id,
                'default_company_id': self.company_id.id,
                'default_doctor_id': self.doctor.id,
                'default_patient_id': self.patient.id,
            }
        }


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    lab_request_id = fields.Many2one('lab.request', 'Attach Results')