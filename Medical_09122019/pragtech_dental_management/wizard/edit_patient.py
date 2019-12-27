from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class EditPatient(models.TransientModel):
    _name = 'edit.patient'

    new_patient_id = fields.Char('New Patient ID', required=True)
    patient_id = fields.Many2one('medical.patient', 'Patient', required=True)

    @api.multi
    def action_confirm(self):
        wizard_vals = self.read()[0]
        if wizard_vals['patient_id']:
            patient = self.env['medical.patient'].browse(wizard_vals['patient_id'][0])
            this_patient_company = patient.company_id
            all_patient_ids = self.env['medical.patient'].search([('company_id', '=', this_patient_company.id)])
            for pat in all_patient_ids:
                if pat.patient_id == wizard_vals['new_patient_id']:
                    raise UserError(_('Patient with ID as %s already exists. Please enter unique ID') % pat.patient_id)
            new_patient_id = wizard_vals['new_patient_id']
            print ("######################################",this_patient_company)
            if this_patient_company.patient_prefix not in new_patient_id:
                raise UserError(_('Please enter valid Prefex (%s) for Patients') % this_patient_company.patient_prefix)
            if not this_patient_company.patient_prefix:
                list_patient_id = []
                patient.write({'patient_id': wizard_vals['new_patient_id']})
                for pat in all_patient_ids:
                    if this_patient_company.patient_prefix in pat.patient_id:
                        patient_file_no =  pat.patient_id[int(0):]
                        if  patient_file_no.isdigit():
                            list_patient_id.append(int(patient_file_no))
                if list_patient_id:
                    number_next_actual = max(list_patient_id)
                    med_patient_code = self.env['ir.sequence'].search([('code', '=', 'medical.patient'),
                                                                       ('company_id', '=', this_patient_company.id)])
                    med_patient_code[0].write({'number_next_actual': number_next_actual + 1})
            if this_patient_company.patient_prefix in new_patient_id:
                len_prefix = len(this_patient_company.patient_prefix)
                if len_prefix:
                    list_patient_id = []
                    patient.write({'patient_id': wizard_vals['new_patient_id']})
                    for pat in all_patient_ids:
                        if this_patient_company.patient_prefix in pat.patient_id:
                            list_patient_id.append(int(pat.patient_id[int(len_prefix):]))
                    if list_patient_id:
                        number_next_actual = max(list_patient_id)
                        med_patient_code = self.env['ir.sequence'].search([('code', '=', 'medical.patient'),
                                                  ('company_id', '=', this_patient_company.id)])
                        med_patient_code[0].write({'number_next_actual': number_next_actual+1})
