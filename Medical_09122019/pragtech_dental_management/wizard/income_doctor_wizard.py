# -*- coding: utf-8 -*-
from odoo import fields, models, api


class IncomeByDoctorReportWizard(models.TransientModel):
    _name = 'income.by.doctor.report.wizard'
   
    start_date = fields.Date('Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date('End Date', required=True, default=fields.Date.context_today)
    
    @api.multi
    def income_by_doctor_report(self):
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        return self.env.ref('pragtech_dental_management.income_byreport_report12333').report_action(self, data=data)


class PatientDoctorReportWizard(models.TransientModel):
    _name = 'patient.by.doctor.report.wizard'
   
    def _get_company_id(self):
        domain_company = []
        company_ids = None
        group_multi_company = self.env.user.has_group('base.group_multi_company')
        if group_multi_company:
            company_ids = [x.id for x in self.env['res.company'].search([('id', 'in', self.env.user.company_ids.ids)])]
            domain_company = [('id', 'in', company_ids)]
        else:
            domain_company = [('id', '=', self.env.user.company_id.id)]
        return domain_company

    company_id = fields.Many2one('res.company', "Company", domain=_get_company_id, required=True)
    start_date = fields.Date('Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date('End Date', required=True, default=fields.Date.context_today)

    @api.model
    def default_get(self, fields):
        res = super(PatientDoctorReportWizard, self).default_get(fields)
        self._get_company_id()
        res['company_id'] = self.env.user.company_id.id
        return res

    @api.multi
    def patient_by_doctor_report(self):
        datas = {'active_ids': self.env.context.get('active_ids', []),
                 'form': self.read(['start_date', 'end_date'])[0]}
        datas['form']['company_id'] = [self.company_id.id, self.company_id.name]
        values = self.env.ref('pragtech_dental_management.patient_byreport_report12333').report_action(self, data=datas)
        return values
