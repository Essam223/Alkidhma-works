from datetime import date
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import time
import base64


class MedicalAppointment(models.Model):
    _name = "medical.appointment"
    _order = "appointment_sdate desc"
    _inherit = ['mail.thread']

    def fun_auto_missed_option(self):
        for appt in self.search([('state', 'in', ('draft', 'confirmed'))]):
            appointment_edate = datetime.strptime(str(appt.appointment_edate), '%Y-%m-%d %H:%M:%S')
            if appointment_edate < datetime.now():
                appt.write({'state':'missed'})

    @api.model
    def get_formview_id(self):
        try:
            view_id = self.env.ref(
                'pragtech_dental_management.medical_appointment_view').id
        except Exception:
            view_id = super(MedicalAppointment, self).get_formview_id()
        return view_id

    @api.multi
    @api.onchange('name')
    def _state_visit_closed(self):
        for appt in self:
            appt.state_visit_closed = 1
            if appt.state in ('done', 'visit_closed'):
                if appt.state == 'done':
                    if not appt.invoice_id:
                        self._cr.execute('UPDATE medical_appointment SET state=%s WHERE id=%s',
                                         ('visit_closed', appt.id))
                    if appt.invoice_id:
                        if appt.invoice_id.state in ('open', 'paid'):
                            self._cr.execute('UPDATE medical_appointment SET state=%s WHERE id=%s',
                                             ('visit_closed', appt.id))
                if appt.state == 'visit_closed':
                    if appt.invoice_id:
                        if appt.invoice_id.state not in ('open', 'paid'):
                            self._cr.execute('UPDATE medical_appointment SET state=%s WHERE id=%s',
                                             ('done', appt.id))

    def delayed_time(self):
        for patient_data in self:
            if patient_data.checkin_time and patient_data.checkin_time > patient_data.appointment_sdate:
                patient_data.delayed = True
            else:
                patient_data.delayed = False

    @api.multi
    @api.depends('checkin_time', 'ready_time')
    def _waiting_time(self):
        def compute_time(checkin_time, ready_time):
            if checkin_time and ready_time:
                ready_time = datetime.strptime(ready_time, '%Y-%m-%d %H:%M:%S')
                checkin_time = datetime.strptime(checkin_time, '%Y-%m-%d %H:%M:%S')
                delta = relativedelta(ready_time, checkin_time)
                years_months_days = str(delta.hours) + "h " + str(delta.minutes) + "m "
            else:
                years_months_days = "No Waiting time !"
            return years_months_days

        for patient_data in self:
            patient_data.waiting_time = compute_time(patient_data.checkin_time, patient_data.ready_time)

    READONLY_STATES_APPOINT = {
        'done': [('readonly', True)],
        'visit_closed': [('readonly', True)],
    }

    READONLY_STATES_INCHAIR = {'draft': [('readonly', False)],
                               'confirmed': [('readonly', False)]}

    READONLY_STATES_CHECKIN = {'draft': [('readonly', False)],
                               'confirmed': [('readonly', False)], 'checkin': [('readonly', False)]}

    @api.multi
    def toggle_active(self):
        if self.active:
            contextt = {}
            contextt['default_appt_id'] = self.id
            return {
                'name': _('Enter Archive Reason'),
                'view_id': self.env.ref('pragtech_dental_management.view_archive_wizard_wizard2').id,
                'type': 'ir.actions.act_window',
                'res_model': 'archive.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': contextt
            }
        else:
            self.active = True

    def find_hcare_groups(self):
        is_group = False
        # Admin/Receptionist
        if self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu') or \
                self.env.user.has_group('pragtech_dental_management.group_dental_user_menu'):
            is_group = True
        return is_group

    def _get_room_Id(self):
        company = self.env['res.company']._company_default_get('res.partner')
        if self.company_id:
            company = self.company_id
        domain = [('company_id', '=', company.id)]
        return domain

    def _get_patient_Id(self):
        company = self.env['res.company']._company_default_get('res.partner')
        if self.company_id:
            company = self.company_id
        domain = [('company_id', '=', company.id)]
        # pat_doc_ids = [x.id for x in self.env['medical.patient'].search(domain)]
        # domain = [('id', 'in', pat_doc_ids)]
        # domain = [('id', 'in', [33,34])]
        return domain

    def _get_doctor_Id(self):
        doc_ids = None
        other_hcare_grps = self.find_hcare_groups()
        if self.env.user.has_group('pragtech_dental_management.group_dental_doc_menu') and not other_hcare_grps:
            partner_ids = [x.id for x in self.env['res.partner'].search([('user_id', '=', self.env.user.id),
                                                                         ('company_id', '=', self.company_id.id),
                                                                         ('is_doctor', '=', True)])]
            if partner_ids:
                doc_ids = [x.id for x in self.env['medical.physician'].search([('company_id', '=', self.company_id.id),
                                                                               ('name', 'in', partner_ids)])]
        else:
            doc_ids = [x.id for x in self.env['medical.physician'].search([('company_id', '=', self.company_id.id)])]
        domain = [('id', 'in', doc_ids)]
        return domain

    @api.model
    def _get_default_doctor(self):
        doc_ids = None
        dom_partner = [('user_id', '=', self.env.user.id), ('is_doctor', '=', True),
                       ('company_id', '=', self.company_id.id)]
        partner_ids = [x.id for x in self.env['res.partner'].search(dom_partner)]
        if partner_ids:
            doc_ids = [x.id for x in self.env['medical.physician'].search([('name', 'in', partner_ids),
                                                                           ('company_id', '=', self.company_id.id)])]
        self._get_doctor_Id()
        return doc_ids

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.doctor and self.doctor.company_id != self.company_id:
            self.doctor = False
        if self.patient and self.patient.company_id != self.company_id:
            self.patient = False
        if self.room_id and self.room_id.company_id != self.company_id:
            self.room_id = False
        room_domain = self._get_room_Id()
        patient_domain = self._get_patient_Id()
        doctor_domain = self._get_doctor_Id()
        return {
            'domain': {
                'room_id': room_domain,
                'patient': patient_domain,
                'doctor': doctor_domain}
        }

    doctor = fields.Many2one('medical.physician', 'Doctor', help="Doctor's Name",
                             required=True,
                             default=_get_default_doctor, readonly=True, states=READONLY_STATES_INCHAIR,
                             track_visibility='onchange', domain=_get_doctor_Id)
    name = fields.Char('Appointment ID', size=64, readonly=True, default=lambda self: _('New'),
                       track_visibility='onchange', copy=False)
    patient = fields.Many2one('medical.patient', 'Patient', help="Patient Name", required=False, readonly=True,
                              states=READONLY_STATES_INCHAIR, track_visibility='onchange', domain=_get_patient_Id)
    patient_partner = fields.Many2one('res.partner', 'Patient Partner', required=False, related= 'patient.name',
                           domain=[('is_patient', '=', True)], help="Patient Name")
    insurance_id = fields.Many2one('medical.insurance', "Insurance", readonly=False,
                                   states=READONLY_STATES_APPOINT, track_visibility='onchange',
                                   domain="[('patient_id','=',patient)]")
    appointment_sdate = fields.Datetime('Appointment Start', required=True, default=fields.Datetime.now,
                                        readonly=False, track_visibility='onchange')
    appointment_edate = fields.Datetime('Appointment End', required=False, readonly=False,
                                        track_visibility='onchange')
    room_id = fields.Many2one('medical.hospital.oprating.room', 'Room', required=False, readonly=False,
                              states=READONLY_STATES_APPOINT, track_visibility='onchange', domain=_get_room_Id)
    urgency = fields.Boolean('Urgent', default=False, readonly=True, states=READONLY_STATES_CHECKIN,
                             track_visibility='onchange')
    comments = fields.Text('Note', readonly=False, track_visibility='onchange')
    checkin_time = fields.Datetime('Checkin Time', track_visibility='onchange')
    ready_time = fields.Datetime('In Chair', track_visibility='onchange')
    waiting_time = fields.Char('Waiting Time', compute='_waiting_time')
    no_invoice = fields.Boolean('Invoice exempt', readonly=False, states=READONLY_STATES_APPOINT,
                                track_visibility='onchange')
    invoice_done = fields.Boolean('Invoice Done', readonly=False, states=READONLY_STATES_APPOINT,
                                  track_visibility='onchange')
    user_id = fields.Many2one('res.users', related='doctor.user_id', string='doctor', store=True,
                              track_visibility='onchange')
    inv_id = fields.Many2one('account.invoice', 'Invoice', readonly=True, track_visibility='onchange')
    state = fields.Selection(
        [('draft', 'Booked'), ('confirmed', 'Confirmed'), ('missed', 'Missed'),
         ('checkin', 'Checked In'), ('ready', 'In Chair'), ('done', 'Completed'),
         ('visit_closed', 'Visit Closed'), ('cancel', 'Canceled')], 'State',
        readonly=True, default='draft', track_visibility='onchange')
    state_visit_closed = fields.Char(compute='_state_visit_closed', string='To find state: completed/visit closed')
    apt_id = fields.Boolean(default=False, track_visibility='onchange')
    patient_state = fields.Selection([('walkin', 'Walk In'), ('withapt', 'Come with Appointment')], 'Patients status',
                                     required=True, default='walkin', readonly=True, states=READONLY_STATES_INCHAIR,
                                     track_visibility='onchange')
    #     treatment_ids = fields.One2many ('medical.lab', 'apt_id', 'Treatments')
    saleperson_id = fields.Many2one('res.users', 'Created By', default=lambda self: self.env.user, readonly=False,
                                    states=READONLY_STATES_APPOINT, track_visibility='onchange')
    delayed = fields.Boolean(compute='delayed_time', string='Delayed', store=True, track_visibility='onchange')
    op_summary_ids = fields.One2many('operation.summary', 'appt_id', 'Activities')
    reason_archive = fields.Text('Reason for Archive', track_visibility='onchange')
    active = fields.Boolean(default=True,
                            help="The active field allows you to hide the appointment without removing it.",
                            track_visibility='onchange')
    operations = fields.One2many('medical.teeth.treatment', 'appt_id', 'Operations',
                                 track_visibility='onchange')
    attachment_ids = fields.One2many('ir.attachment', 'appointment_id', 'attachments', track_visibility='onchange')
    patient_name = fields.Char("Patient Name", readonly=False, states=READONLY_STATES_APPOINT,
                               track_visibility='onchange')
    patient_phone = fields.Char("Patient Phone", readonly=False, states=READONLY_STATES_APPOINT,
                                track_visibility='onchange')
    qid = fields.Char("QID", track_visibility='onchange')
    sex = fields.Selection([('m', 'Male'), ('f', 'Female'), ], 'Gender', track_visibility='onchange')
    dob = fields.Date('Date of Birth', track_visibility='onchange')
    nationality_id = fields.Many2one('patient.nationality', 'Nationality', track_visibility='onchange')
    is_registered = fields.Boolean("Is a registered patient?", readonly=True, states=READONLY_STATES_INCHAIR,
                                   track_visibility='onchange')
    followup = fields.Boolean("Follow up", track_visibility='onchange', default=False)
    treatment_ids = fields.One2many("treatment.invoice", 'appointment_id', "Treatments", readonly=False,
                                    states=READONLY_STATES_APPOINT, track_visibility='onchange')
    finding_ids = fields.One2many("complaint.finding", 'appt_id', "Complaints and findings", readonly=False,
                                  track_visibility='onchange')
    prescription_ids = fields.One2many("prescription.line", 'appt_id', "Prescriptions", readonly=False,
                                       track_visibility='onchange')
    invoice_id = fields.Many2one("account.invoice", "Invoice entry", readonly=True, track_visibility='onchange',
                                 copy=False)
    invoice_count = fields.Integer(string='# of Invoices', compute='_get_invoiced', readonly=True)
    invoice_ids = fields.Many2many("account.invoice", string='Invoices', compute="_get_invoiced", readonly=True,
                                   copy=False)
    payment_count = fields.Integer(string='# of Payments', compute='_get_payments', readonly=True)
    payment_ids = fields.Many2many("account.payment", string='Payments', compute="_get_payments", readonly=True,
                                   copy=False)
    amount_due = fields.Char('Outstanding Amount', compute='_get_invoiced')
    amount_advance = fields.Char('Advance Amount', compute='_get_invoiced')
    plan_signature = fields.Binary(string='Signature')
    treatment_plan_date = fields.Date(string="Treatment Plan Date", track_visibility='onchange')
    hav_operation = fields.Boolean("Have operation?", compute='_get_hav_operation')
    hav_prescription = fields.Boolean("Have Prescription?", compute='_get_hav_prescription')
    attach_count = fields.Integer(string='# of Attachments', compute='_get_attached', readonly=True)
    reason_reversal = fields.Text('Reason for Invoice Reversal', track_visibility='onchange')
    medicl_history = fields.Text('Medical/Surgical History')
    benefit_type = fields.Selection([('Dental', 'Dental'), ('Orthodontic', 'Orthodontic'),
                                     ('Dental_Orthodontic', 'Dental and Orthodontic') ], 'Benefit type',
                                    track_visibility='onchange', default='Dental')
    responsible_person = fields.Many2one('res.users', string='Responsible Person', track_visibility='onchange')

    highlight_color = fields.Char('Highlight Color', default="ff000c")


    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')

    company_id = fields.Many2one('res.company', 'Company', index=True, default=_default_company, readonly=True,
                                 states=READONLY_STATES_INCHAIR, track_visibility='onchange')

    @api.constrains('company_id', 'name', 'room_id', 'doctor', 'patient')
    def _check_same_company_appt(self):
        if self.company_id:
            if self.doctor.company_id:
                if self.company_id.id != self.doctor.company_id.id:
                    raise ValidationError(_('Error ! Doctor and Appointment should be of same company'))
            if self.patient.company_id:
                if self.company_id.id != self.patient.company_id.id:
                    raise ValidationError(_('Error ! Patient and Appointment should be of same company'))
            if self.room_id.company_id:
                if self.company_id.id != self.room_id.company_id.id:
                    raise ValidationError(_('Error ! Room and Appointment should be of same company'))

    _sql_constraints = [
        ('date_check', "CHECK (appointment_sdate <= appointment_edate)",
         "Appointment Start Date must be before Appointment End Date !"), ]

    @api.multi
    def get_date(self, date1, lang):
        new_date = ''
        if date1:
            search_id = self.env['res.lang'].search([('code', '=', lang)])
            new_date = datetime.strftime(datetime.strptime(date1, '%Y-%m-%d %H:%M:%S').date(), search_id.date_format)
        return new_date

    @api.multi
    def cancel(self):
        return self.write({'state': 'cancel', 'responsible_person':self.env.user.id})

    @api.multi
    def confirm_appointment(self):
        return self.write({'state': 'confirmed'})

    @api.multi
    def ready(self):
        ready_time = time.strftime('%Y-%m-%d %H:%M:%S')
        self.write({'state': 'ready', 'ready_time': ready_time})
        return True

    @api.multi
    def open_quest_format(self):
        return {
            'name': _('Questionnaire Form'),
            'type': 'ir.actions.act_window',
            'res_model': 'questionnaire.format.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': False,
            'context': {}
        }

    @api.multi
    def missed(self):
        self.write({'state': 'missed'})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            appt_seq = self.env['ir.sequence'].search([('code', '=', 'medical.appointment'),
                                                          ('company_id', '=', self.env.user.company_id.id)])
            if not appt_seq:
                raise UserError(_("You have to define a sequence for %s in your company: %s.")
                                % ('medical.appointment', self.env.user.company_id.name))
            vals['name'] = appt_seq.next_by_code('medical.appointment')
            # vals['name'] = self.env['ir.sequence'].next_by_code('medical.appointment') or 'New'
        result = super(MedicalAppointment, self).create(vals)
        if result.patient_state == 'walkin':
            result.checkin()
        if 'patient' in list(vals.keys()) and vals['patient']:
            self._cr.execute('insert into pat_apt_rel(patient,apid) values (%s,%s)', (vals['patient'], result.id))
        return result

    @api.multi
    def print_prescription(self):
        datas = {'ids': self.ids}
        values = self.env.ref('pragtech_dental_management.prescription_report2').report_action(self, data=datas)
        return values

    @api.depends('name', 'patient', 'prescription_ids')
    def _get_hav_prescription(self):
        for appt in self:
            check_hav_prescrption = False
            for i in appt.prescription_ids:
                check_hav_prescrption = True
            appt.update({
                'hav_prescription': check_hav_prescrption
            })

    @api.depends('name', 'patient')
    def _get_hav_operation(self):
        for appt in self:
            check_hav_operation = False
            if appt.patient:
                for i in appt.patient.teeth_treatment_ids:
                    if i.state == 'planned':
                        check_hav_operation = True
            appt.update({
                'hav_operation': check_hav_operation
            })

    @api.multi
    def attach_treatment_plan(self):
        data = {'ids': self.ids}
        patient = ""
        if self.patient:
            patient = self.patient.name_get()[0][1]
        data, data_format = self.env.ref('pragtech_dental_management.report_treatment_plan2_pdf').render(self.ids,
                                                                                                         data=data)
        att_id = self.env['ir.attachment'].create({
            'name': 'Treatment_Plan_' + self.treatment_plan_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': patient + '_treatment_plan.pdf',
            'res_model': 'medical.appointment',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def action_Reverse(self):
        is_only_doctor = False
        group_dental_doc_menu = self.env.user.has_group('pragtech_dental_management.group_dental_doc_menu')
        group_dental_mng_menu = self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu')
        if group_dental_doc_menu and not group_dental_mng_menu:
            is_only_doctor = True
        if self.invoice_id:
            if self.invoice_id.state in ('open', 'paid') and is_only_doctor:
                raise ValidationError('The invoice of this appointment is already processed. '
                                      'Please contact administrator to reopen..')
        contextt = {}
        contextt['default_appt_id'] = self.id
        appt = self
        list_inv_Credit = []
        if appt.invoice_id:
            list_inv_Credit.append(appt.invoice_id)
            if appt.invoice_id.number:
                credit_note = self.env['account.invoice'].search([('origin', '=', appt.invoice_id.number)])
                for c_note in credit_note:
                    list_inv_Credit.append(c_note)
        msg = ""
        if list_inv_Credit:
            msg = "Upon Confirmation , System will Cancel "
        for inv_Cred in list_inv_Credit:
            if inv_Cred.type == 'out_refund':
                msg += " and a Credit Note"
            else:
                msg += "an Invoice"
            if inv_Cred.number:
                msg += _("(") + " %s " % (inv_Cred.number) + _(")")
        contextt['default_warning_msg'] = msg
        return {
            'name': _('Enter Reversal Reason'),
            'view_id': self.env.ref('pragtech_dental_management.view_completed_reversal_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'completed.reversal',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def done(self):
        treatment_ids = self.treatment_ids
        invoice_vals = {}
        invoice_line_vals = []
        # each_line = [0, False]
        # product_dict = {}
        inv_id = False
        patient_brw = self.patient
        partner_brw = patient_brw.name
        jr_brw = self.env['account.journal'].search([('type', '=', 'sale'), ('name', '=', 'Customer Invoices'), ('company_id', '=', self.company_id.id)])
        cost_center_id = False
        if self.doctor:
            if self.doctor.department_id:
                if self.doctor.department_id:
                    cost_center_id = self.doctor.department_id.cost_center_id.id
        if treatment_ids:
            for each in treatment_ids:
                each_line = [0, False]
                product_dict = {}
                product_dict['product_id'] = each.description.id
                p_brw = each.description
                if each.note:
                    product_dict['name'] = each.note
                else:
                    product_dict['name'] = each.description.name
                product_dict['quantity'] = 1
                if each.amount < each.actual_amount:
                    product_dict['discount_fixed_percent'] = 'Fixed'
                    product_dict['discount_value'] = each.actual_amount - each.amount
                    product_dict['price_unit'] = each.actual_amount
                else:
                    product_dict['price_unit'] = each.amount
                acc_obj = self.env['account.account'].search([('name', '=', 'Local Sales'),
                                                              ('user_type_id', '=', 'Income')], limit=1)
                for account_id in jr_brw:
                    product_dict[
                        'account_id'] = account_id.default_debit_account_id.id if account_id.default_debit_account_id else acc_obj.id
                product_dict['cost_center_id'] = cost_center_id
                each_line.append(product_dict)
                invoice_line_vals.append(each_line)
            # Creating invoice dictionary
            invoice_vals['date_invoice'] = self.appointment_sdate
            if partner_brw.property_account_receivable_id.company_id != self.patient.company_id:
                company_id = self.company_id.id
                company_browse = self.env['res.company'].browse(company_id)
                receiv_val_ref, payable_val_ref = company_browse.get_account_receiv_payable(company_id)
                partner_brw.write({'property_account_receivable_id':int(receiv_val_ref),
                                   'property_account_payable_id': int(payable_val_ref)})
            invoice_vals['account_id'] = partner_brw.property_account_receivable_id.id
            invoice_vals['company_id'] = self.company_id.id
            invoice_vals['journal_id'] = jr_brw.id
            invoice_vals['partner_id'] = partner_brw.id
            invoice_vals['dentist'] = self.doctor.id
            invoice_vals['cost_center_id'] = cost_center_id
            invoice_vals['is_patient'] = True
            invoice_vals['appt_id'] = self.id
            invoice_vals['insurance_card'] = self.insurance_id.id
            invoice_vals['insurance_company'] = self.insurance_id.company_id.id
            invoice_vals['invoice_line_ids'] = invoice_line_vals
            inv_id = self.env['account.invoice'].create(invoice_vals)
        if inv_id:
            vals = {'state': 'done'}
            vals['invoice_id'] = inv_id.id
        if not inv_id:
            vals = {'state': 'visit_closed'}
        return self.write(vals)

    @api.onchange('is_registered')
    def _onchange_is_registered_field(self):
        for rec in self:
            if rec.is_registered:
                rec.patient = False
                rec.patient_phone = False
                rec.patient_name = False
                rec.qid = False
            else:
                rec.patient = False
                rec.patient_phone = False
                rec.patient_name = False
                rec.qid = False

    @api.onchange('qid')
    def get_patient_data_from_qid(self):
        patient_data = self.env['medical.patient'].search([('qid', '=', self.qid),('qid', '!=', False)], limit=1)
        if patient_data and self.is_registered:
            self.patient = patient_data.id

    @api.multi
    def appt_open_chart(self):
        if self.patient:
            ctx = dict(self.env.context)
            ctx.update({
                'appointment': self.id,
                'insurance': self.insurance_id and self.insurance_id.id or False,
                'doctor': self.doctor and self.doctor.id or False,
		'highlight_color': self.highlight_color,
            })
            result = self.patient.with_context(ctx).open_chart()
            return result

    @api.multi
    def show_inv_due(self):
        pass

    @api.multi
    def show_advance(self):
        pass

    @api.onchange('appointment_sdate')
    def onchange_appointment_sdate(self):
        for rec in self:
            if rec.appointment_sdate:
                date_start = datetime.strptime(str(rec.appointment_sdate), '%Y-%m-%d %H:%M:%S')
                rec.appointment_edate = date_start + timedelta(minutes=15)

    @api.onchange('patient')
    def onchange_patient(self):
        for rec in self:
            if (rec.patient and rec.patient.company_id != rec.company_id) or not rec.patient:
                rec.patient = False
                rec.patient_name = False
                rec.patient_phone = False
                rec.qid = False
            if rec.patient:
                rec.patient_name = rec.patient.name.name
                rec.patient_phone = rec.patient.mobile
                rec.qid = rec.patient.qid
                rec.is_registered = True

    def funct_followup(self, patient, appointment_sdate, doctor, name):
        is_follow_up = 0
        is_expired_up = 0
        if patient and appointment_sdate and doctor:
            patient = self.env['medical.patient'].browse(int(patient))
            doctor = self.env['medical.physician'].browse(int(doctor))
            appointment_sdate = datetime.strptime(appointment_sdate, "%Y-%m-%d %H:%M:%S")
            x_days_before = appointment_sdate - timedelta(days=doctor.followup_days)
            double_x_days_before = appointment_sdate - timedelta(days=2*doctor.followup_days)
            not_follow_up_appts = self.env['medical.appointment'].search([('patient', '=', patient.id),
                                                          ('doctor', '=', doctor.id),
                                                          ('followup', '=', False),
                                                          ('name', '!=', name),
                                                          ('state', 'in', ('done', 'visit_closed')),
                                                          ('appointment_sdate', '>=', str(x_days_before)),
                                                          ('appointment_sdate', '<', str(appointment_sdate)),
                                                          ])
            follow_up_appts = self.env['medical.appointment'].search([('patient', '=', patient.id),
                                                          ('doctor', '=', doctor.id),
                                                          ('followup', '=', True),
                                                          ('name', '!=', name),
                                                          ('state', 'in', ('done', 'visit_closed')),
                                                          ('appointment_sdate', '>=', str(x_days_before)),
                                                          ('appointment_sdate', '<', str(appointment_sdate)),
                                                          ])
            expired_appts = self.env['medical.appointment'].search([('patient', '=', patient.id),
                                                                 ('doctor', '=', doctor.id),
                                                                 ('followup', '=', False),
                                                                 ('name', '!=', name),
                                                                ('state', 'in', ('done', 'visit_closed')),
                                                                 ('appointment_sdate', '>=', str(double_x_days_before)),
                                                                 ('appointment_sdate', '<',str(x_days_before)),
                                                                 ])
            if not_follow_up_appts:
                if not follow_up_appts:
                    is_follow_up = 1
                    return [is_follow_up, is_expired_up]
                else:
                    is_follow_up = 0
                    return [is_follow_up, is_expired_up]
            elif expired_appts:
                is_follow_up = 0
                is_expired_up = 1
                return [is_follow_up, is_expired_up]
            else:
                return [is_follow_up, is_expired_up]
        return [is_follow_up, is_expired_up]

    @api.onchange('patient', 'appointment_sdate', 'doctor')
    def get_followup_patient(self):
        for rec in self:
            is_follow_up, is_expired_up = rec.funct_followup(rec.patient.id, rec.appointment_sdate, rec.doctor.id, rec.name)
            if is_follow_up == 1:
                rec.followup = True
                message = 'This can be a followup visit'
                # self.env.user.notify_info(message, title='Followup Info', sticky=True)
            else:
                rec.followup = False
                if is_expired_up == 1:
                    message = 'Followup expired'
                    # self.env.user.notify_info(message, title='Followup Info', sticky=True)
                else:
                    message =  'This is not a followup visit'
                    # self.env.user.notify_info(message, title='Followup Info', sticky=True)

    @api.multi
    def unlink(self):
        for rec in self:
            raise ValidationError(_('You cannot delete Appointments.'))
        return super(MedicalAppointment, self).unlink()

    @api.multi
    def write(self, vals):
        if 'patient' in list(vals.keys()):
            qry = """SELECT * FROM pat_apt_rel WHERE apid = %s"""
            self._cr.execute(qry, [self.id])
            res = self._cr.fetchall()
            if res:
                self._cr.execute('UPDATE pat_apt_rel SET patient=%s WHERE apid=%s', (vals['patient'], self.id))
            else:
                self._cr.execute('insert into pat_apt_rel(patient,apid) values (%s,%s)', (vals['patient'], self.id))
        return super(MedicalAppointment, self).write(vals)

    @api.multi
    def confirm(self):
        for rec in self:
            rec.write({'state': 'confirmed'})

    @api.multi
    def treatment_plan(self):
        appt = self.id
        doctor = ""
        patient = ""
        if self.patient_id:
            patient = self.patient.patient_name
        if self.dentist:
            doctor = self.dentist.name.name
        return {
            'name': _('Treatment Plan'),
            'type': 'ir.actions.act_window',
            'res_model': 'treatment.sign.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': False,
            'context': {
                'default_appt_id': appt,
                'default_doctor': doctor,
                'default_patient': patient,
            }
        }

    @api.multi
    def questionnaire_popup(self):
        if self.patient:
            language = 'english'
            if self.patient.language:
                language = self.patient.language
            return {
                'name': _('Registration Form'),
                'type': 'ir.actions.act_window',
                'res_model': 'patient.registration',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'nodestroy': False,
                'context': {
                    'default_patient_id': self.patient.id,
                    'default_language': language,
                    'default_emergency_name': self.patient.emergency_name,
                    'default_emergency_phone': self.patient.emergency_phone,
                    'default_emergency_relation': self.patient.emergency_relation,
                    'default_dob': self.patient.dob,
                    'default_qid': self.patient.qid,
                    'default_address': self.patient.address,
                    'default_other_mobile': self.patient.other_mobile,
                    'default_mobile': self.patient.mobile,
                    'default_patient_name': self.patient.patient_name,
                    'default_name_tag': self.patient.name_tag,
                }
            }

    @api.multi
    def set_back(self):
        for rec in self:
            if self.state == 'confirmed':
                rec.write({'state': 'draft'})
            elif self.state == 'missed':
                rec.write({'state': 'confirmed'})
            if self.state == 'checkin':
                rec.write({'state': 'confirmed'})
            if self.state == 'ready':
                rec.write({'state': 'checkin'})
            if self.state == 'cancel':
                rec.write({'state': 'draft'})

    def checkin(self):
        checkin_time = time.strftime('%Y-%m-%d %H:%M:%S')
        self.write({'state': 'checkin', 'checkin_time': checkin_time})
        if self.doctor:
            doctor_partner = self.doctor.name
            for user in self.env['res.users'].search([]):
                if user.partner_id == doctor_partner:
                    checkin_local = datetime.strptime(checkin_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=3)
                    checkin_local = datetime.strftime(checkin_local, '%I:%M:%S %p')
                    message = self.patient_name + " checked In at " + str(checkin_local)
                    info_title = 'Patient Checked In'
                    if self.urgency:
                        info_title = 'Emergency Patient Checked In'
                        message = message + ". Please do the needful !!"
                    user.notify_info(message, title=info_title, sticky=True)

        if not self.patient:
            values_partner = {'name': self.patient_name,
                              'phone': self.patient_phone,
                              'is_patient': True,
                             }
            values_patient = {'patient_name': self.patient_name,
                              'register_date': date.today(),
                              'mobile': self.patient_phone,
                              'qid': self.qid,
                              'sex': self.sex,
                              'dob': self.dob,
                              'nationality_id': self.nationality_id.id,
                             }
            company_id = self.company_id.id
            if company_id:
                company_browse = self.env['res.company'].browse(company_id)
                values_partner = company_browse.update_partner_receiv_payable(company_id, values_partner)
                values_patient['company_id'] = company_id
            partner_id = self.env['res.partner'].create(values_partner)
            values_patient['name'] = partner_id.id
            patient_id = self.env['medical.patient'].create(values_patient)
            self.patient = patient_id
            # return {
            #     'name': _('Patient Details'),
            #     'view_mode': 'form',
            #     'view_id':  self.env.ref('pragtech_dental_management.medical_patient_view').id,
            #     'res_model': 'medical.patient',
            #     'type': 'ir.actions.act_window',
            #     'res_id': patient_id.id,
            #     'target': 'form',
            # }

    @api.depends('name')
    def _get_payments(self):
        for appt in self:
            if appt.patient:
                patient = appt.patient
                payment_ids = self.env['account.payment'].search([('partner_id', '=', patient.name.id),
                                                                  ('partner_type', '=', 'customer')])
                appt.update({
                    'payment_count': len(set(payment_ids.ids)),
                    'payment_ids': payment_ids.ids
                })
            else:
                appt.update({
                    'payment_count': 0,
                    'payment_ids': []
                })

    @api.multi
    def action_view_payment(self):
        payments = self.mapped('payment_ids')
        action = self.env.ref('account.action_account_payments').read()[0]
        if len(payments) > 1:
            action['domain'] = [('id', 'in', payments.ids)]
        elif len(payments) == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = payments.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def show_attachments(self):
        attachments = self.mapped('attachment_ids')
        action = self.env.ref('pragtech_dental_management.action_attachments').read()[0]
        if len(attachments) > 0:
            action['domain'] = [('id', 'in', attachments.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.depends('name', 'patient')
    def _get_invoiced(self):
        for appt in self:
            if appt.patient:
                patient = appt.patient
                invoice_ids = self.env['account.invoice'].search([('partner_id', '=', patient.name.id),
                                                                  ('type', '=', 'out_invoice')])
                amount_due = 0
                for inv in invoice_ids:
                    amount_due += inv.residual_signed
                domain = [('account_id', '=', appt.patient.name.property_account_receivable_id.id),
                          ('partner_id', '=', appt.patient.name.id),
                          ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
                          ('amount_residual_currency', '!=', 0.0),
                          ('credit', '>', 0), ('debit', '=', 0)]
                lines = self.env['account.move.line'].search(domain)
                advance = 0
                if len(lines) != 0:
                    for line in lines:
                        amount_to_show = line.company_id.currency_id.with_context(date=line.date).compute(
                            abs(line.amount_residual), self.env.user.company_id.currency_id)
                        advance += amount_to_show
                appt.update({
                    'invoice_count': len(set(invoice_ids.ids)),
                    'invoice_ids': invoice_ids.ids,
                    'amount_due': "{:.2f}".format(amount_due),
                    'amount_advance': "{:.2f}".format(advance)
                })
            else:
                appt.update({
                    'invoice_count': 0,
                    'invoice_ids': []
                })

    @api.depends('attachment_ids')
    def _get_attached(self):
        for appt in self:
            if appt.attachment_ids:
                attach_count = self.env['ir.attachment'].search_count([('appointment_id', '=', appt.id)])
                appt.update({
                    'attach_count': attach_count,
                })
            else:
                appt.update({
                    'attach_count': 0,
                })

    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['context'] = {'hide_for_service_bill': True, 'show_for_service_bill': True}
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def get_img(self):
        for rec in self:
            res = {}
            img_lst_ids = []
            imd = self.env['ir.model.data']
            action_view_id = imd.xmlid_to_res_id('action_result_image_view')
            for i in rec.attachment_ids:
                img_lst_ids.append(i.id)
            res['image'] = img_lst_ids

            return {
                'type': 'ir.actions.client',
                'name': 'Appointment image',
                'tag': 'result_images',
                'params': {
                    'patient_id': rec.id or False,
                    'model': 'medical.appointment',
                    'values': res
                },
            }
