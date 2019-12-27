# -*- coding: utf-8 -*-

from odoo import api, fields, exceptions, models, SUPERUSER_ID, _


def update_appointment_color(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("select color, state "
               "from appointment_state_color")
    temp = cr.dictfetchall()
    state_color = {}
    for state in temp:
        state_color[state['state']] = state['color']

    apt_rec = env['medical.appointment'].search([])

    for i in apt_rec:
        i.write({'color': state_color[i.state]})
        # updating patient data
        if i.patient:
            if i.patient.patient_name and i.patient.mobile:
                i.update({
                    'patient_name_phone': (i.patient.patient_name + ' : ' +
                                           i.patient.mobile)
                })
        else:
            if i.patient_name and i.patient_phone:
                i.update({
                    'patient_name_phone': (i.patient_name + ' : ' +
                                           i.patient_phone)
                })
            elif i.patient_name:
                i.update({
                    'patient_name_phone': i.patient_name
                })
            else:
                i.update({
                    'patient_name_phone': i.patient_phone
                })


class AppointmentColorConfig(models.Model):
    _name = 'appointment.state.color'

    state = fields.Selection([
        ('draft', 'Booked'), ('confirmed', 'Confirmed'), ('missed', 'Missed'),
        ('checkin', 'Checked In'), ('ready', 'In Chair'),
        ('done', 'Completed'),
        ('visit_closed', 'Visit Closed'), ('cancel', 'Canceled')
    ], string="Status")
    color = fields.Char(string="Color")


class AppointmentExtended(models.Model):
    _inherit = 'medical.appointment'

    color = fields.Char(default='rgba(115,138,230,0.59)',
                        compute='_get_color',
                        store=True)
    patient_file_no = fields.Char(
        related='patient.patient_id',
        store=True)
    # patient_phone = fields.Char(
    #     related='patient.mobile',
    #     store=True)
    # patient_name = fields.Char(
    #     related='patient.patient_name',
    #     store=True)
    patient_name_phone = fields.Char(
        compute='_get_patient_data',
        store=True)
    doctor_user = fields.Char(compute='find_is_doctor')

    # @api.model
    # def create(self, vals):
    #     if ('is_registered' in vals.keys()
    #             and not vals['is_registered'] and
    #             ('sex' in vals.keys() or 'dob' in vals.keys())):
    #         # this portion is created for the appointment creation
    #         # from the scheduler, for the unregistered patients,
    #         # we will create a new patient record
    #         patient_rec = self.env['medical.patient'].create({
    #             'patient_name': vals.get('patient_name'),
    #             'mobile': vals.get('patient_phone'),
    #             'qid': vals.get('qid'),
    #             'sex': vals.get('sex'),
    #             'dob': vals.get('dob'),
    #         })
    #         vals['patient'] = patient_rec.id
    #         vals['patient_file_no'] = patient_rec.patient_id
    #     res = super(AppointmentExtended, self).create(vals)
    #     return res

    @api.depends('patient')
    @api.multi
    def find_is_doctor(self):
        if self.env.user.has_group(
                'pragtech_dental_management.group_dental_doc_menu'):
            for rec in self:
                rec.doctor_user = 'True'
        else:
            for rec in self:
                rec.doctor_user = 'False'

    @api.depends('patient')
    @api.multi
    def _get_patient_data(self):
        for appt in self:
            if appt.patient:
                if appt.patient.patient_name and appt.patient.mobile:
                    appt.update({
                        'patient_name_phone': (
                                    appt.patient.patient_name + ' : ' +
                                    appt.patient.mobile)
                    })
                elif appt.patient.patient_name:
                    appt.update({
                        'patient_name_phone': appt.patient.patient_name
                    })
                elif appt.patient.mobile:
                    appt.update({
                        'patient_name_phone': appt.patient.mobile
                    })

            else:
                if appt.patient_name and appt.patient_phone:
                    appt.update({
                        'patient_name_phone': (appt.patient_name + ' : ' +
                                               appt.patient_phone)
                    })
                elif appt.patient_name:
                    appt.update({
                        'patient_name_phone': appt.patient_name
                    })
                elif appt.patient_phone:
                    appt.update({
                        'patient_name_phone': appt.patient_phone
                    })

    @api.depends('state')
    @api.multi
    def _get_color(self):
        for appt in self:
            if appt.state:
                state_obj = self.env['appointment.state.color'].search(
                    [('state', '=', appt.state)], limit=1)
                if state_obj:
                    appt.update({
                        'color': state_obj.color
                    })


class PatientExt(models.Model):
    _inherit = 'medical.patient'

    @api.onchange('patient_name')
    def onchange_patient_name(self):
        for rec in self:
            if rec.patient_name and rec.name:
                rec.name.name = rec.patient_name
                rec.name.write({'name': rec.patient_name})

            for appt in rec.apt_id:
                new_val = ""
                if rec.patient_name and rec.mobile:
                    new_val = rec.patient_name + ":" + rec.mobile
                elif rec.patient_name:
                    new_val = rec.patient_name
                elif rec.mobile:
                    new_val = rec.mobile
                self._cr.execute(
                    'UPDATE medical_appointment '
                    'SET patient_name_phone=%s WHERE id=%s',
                    (new_val, appt.id))

    @api.onchange('mobile')
    def onchange_mobilee(self):
        for rec in self:
            if rec.mobile:
                for appt in rec.apt_id:
                    new_val = ""
                    if rec.patient_name and rec.mobile:
                        new_val = rec.patient_name + ":" + rec.mobile
                    elif rec.patient_name:
                        new_val = rec.patient_name
                    elif rec.mobile:
                        new_val = rec.mobile
                    self._cr.execute(
                        'UPDATE medical_appointment '
                        'SET patient_phone=%s, patient_name_phone=%s '
                        'WHERE id=%s',
                        (rec.mobile, new_val, appt.id))

    @api.model
    def fetch_patients(self):
        cr = self._cr
        # fetching patients
        cr.execute("SELECT rp.name, mp.id, mp.qid, rp.mobile, mp.patient_id, "
                   "mp.sex, mp.dob, mp.nationality_id "
                   "FROM medical_patient mp "
                   "JOIN res_partner rp  ON(mp.name=rp.id) "
                   "WHERE mp.name IS NOT NULL ")
        patients = cr.dictfetchall()
        return patients
