# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MedicalPhysician(models.Model):
    _name = "medical.physician"
    _description = "Information about the doctor"

    @api.multi
    @api.depends('name')
    def name_get(self):
        result = []
        for partner in self:
            name = partner.name.name
            result.append((partner.id, name))
        return result

    @api.multi
    @api.onchange('name')
    def _domain_partner(self):
        for rec in self:
            rec._get_name_dom_Id()
            rec.domain_partner = 1

    def _get_name_dom_Id(self):
        all_doctors = []
        for all_doc in self.env['res.partner'].search([('is_doctor', '=', "1")]):
            all_doctors.append(all_doc.id)
        for doctor in self.search([]):
            if doctor.name.id in all_doctors:
                all_doctors.remove(doctor.name.id)
        domain = [('id', 'in', all_doctors)]
        return domain

    @api.multi
    def _my_patients(self):
        for rec in self:
            my_appts = self.env['medical.appointment'].search([('doctor', '=', rec.id)])
            patient_list = []
            for appt in my_appts:
                if appt.patient.id not in patient_list:
                    patient_list.append(appt.patient.id)
            my_appt_patient_ids = patient_list
            rec.my_patient_ids = my_appt_patient_ids

    name = fields.Many2one('res.partner', 'Physician', required=True, domain=_get_name_dom_Id,
                           help="Physician's Name, from the partner list")
    domain_partner = fields.Char(compute='_domain_partner')
    code = fields.Char('ID', size=128, help="MD License ID")
    speciality = fields.Many2one('medical.speciality', 'Specialty', required=True, help="Specialty Code")
    license_code = fields.Char(string="Licence No", required=False, track_visibility='onchange')
    info = fields.Text('Extra info')
    user_id = fields.Many2one('res.users', related='name.user_id', string='Physician User', store=True)
    active = fields.Boolean("Active Doctor", default=True)
    followup_days = fields.Integer("Follow up Days")
    stamp = fields.Binary("Stamp and Seal")
    treatment_category = fields.Many2many('product.category', string='Treatment Categores')
    my_patient_ids = fields.Many2many('medical.patient', compute='_my_patients')

    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')

    company_id = fields.Many2one('res.company', 'Company', index=True, default=_default_company)

    @api.model
    def action_my_patients(self):
        action = self.env.ref('pragtech_dental_management.medical_patient_action_tree').read()[0]
        domain = [('id', 'in', [])]
        doctor = False
        if self.env['res.users'].has_group('pragtech_dental_management.group_dental_doc_menu'):
            partner_ids = [x.id for x in self.env['res.partner'].search(
                               [('user_id', '=', self.env.user.id), ('is_doctor', '=', True)])]
            if partner_ids:
                doc_ids = [x for x in self.env['medical.physician'].search([('name', 'in', partner_ids)])]
                if doc_ids:
                    doctor = doc_ids[0]
        if doctor:
            my_patient_ids = doctor.my_patient_ids
            if len(my_patient_ids) > 1:
                domain  = [('id', 'in', my_patient_ids.ids)]
        action['domain'] = domain
        return action
