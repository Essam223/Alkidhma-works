# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InsurancePlan(models.Model):
    _name = "medical.insurance.plan"

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for insurance in self:
            name = insurance.code + ' ' + insurance.name.name
            result.append((insurance.id, name))
        return result

    is_default = fields.Boolean(string='Default Plan',
                                help='Check if this is the default plan when '
                                     'assigning this insurance company to a patient')
    name = fields.Many2one('product.product', string='Plan', required=True,
                           domain="[('type', '=', 'service')]",
                           help='Insurance company plan')
    company_id = fields.Many2one('res.partner', string='Insurance Company', required=True,
                                 domain="[('is_insurance_company', '=', '1')]")
    notes = fields.Text('Extra info')
    code = fields.Char(size=64, required=True, index=True)


class MedicalInsurance(models.Model):
    _name = "medical.insurance"

    @api.multi
    @api.depends('code', 'description')
    def name_get(self):
        result = []
        for med_ins in self:
            name = med_ins.company_id.name or ''
            if med_ins.number:
                name += ':' + med_ins.number
            result.append((med_ins.id, name))
        return result

    name = fields.Many2one('res.partner', string='Member', required=True, domain=[('is_patient', '=', True)])
    patient_id = fields.Many2one('medical.patient', 'Patient', required=True)
    number = fields.Char('Policy Number', size=64, required=True)
    group_name = fields.Char('Group Name')
    insurance_id_no = fields.Char('Member ID')

    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')

    res_company_id = fields.Many2one('res.company', 'Company', index=True, default=_default_company)
    company_id = fields.Many2one('res.partner', 'Insurance Company',required=True,
                                 domain="[('company_id','=',res_company_id), ('is_insurance_company', '=', '1')]")
    member_since = fields.Date('Valid from')
    member_exp = fields.Date('Valid To')
    category = fields.Char('Category', size=64, help="Insurance company plan / category")
    type = fields.Selection([('state', 'State'), ('labour_union', 'Labour Union / Syndical'), ('private', 'Private'), ],
                            'Insurance Type')
    notes = fields.Text('Extra Info')
    plan_id = fields.Many2one('medical.insurance.plan', 'Plan', help='Insurance company plan')
    co_payment_method = fields.Selection([('Amount', 'Amount'), ('Percentage', 'Percentage')],
                                         'Co-payment Method', default='Percentage', required=True)
    amt_paid_by_patient = fields.Float('Co-payment(%)', default=0)
    amt_fixed_paid_by_patient = fields.Float('Co-payment')
    is_deductible = fields.Boolean('Is Deductible?', related='company_id.is_deductible')
    deductible = fields.Float('Deductible', default=0)


    @api.onchange('amt_paid_by_patient')
    @api.depends('amt_paid_by_patient')
    def onchange_amt_paid_by_patient(self):
            if self.amt_paid_by_patient > 100:
                raise UserError('Co-payment(%) should not be greater than 100')
            self.amt_paid_by_insurance = 100 - self.amt_paid_by_patient

    @api.model
    def create(self, vals):
        if vals.get('amt_paid_by_patient') > 100:
                raise UserError('Co-payment(%) should not be greater than 100')
        return super(MedicalInsurance, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(MedicalInsurance, self).write(vals)
        if self.amt_paid_by_patient > 100:
            raise UserError('Co-payment(%) should not be greater than 100')
        return res

    @api.onchange('name')
    def onchange_name(self):
        self.patient_id = False
        if self.name:
            patient_exist = self.env['medical.patient'].search([('name', '=', self.name.id)])
            if patient_exist:
                self.patient_id = patient_exist[0]