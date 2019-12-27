from odoo import models, fields, api


class PatientByProcedureWizard(models.TransientModel):
    _name = 'patient.by.procedure.wizard'
    _description = 'Patient By Procedure Wizard'

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
    date_start = fields.Date('From Date',required=True, default=fields.Date.context_today)
    date_end = fields.Date('To Date',required=True, default=fields.Date.context_today)

    @api.model
    def default_get(self, fields):
        res = super(PatientByProcedureWizard, self).default_get(fields)
        self._get_company_id()
        res['company_id'] = self.env.user.company_id.id
        return res

    @api.multi
    def print_report(self):
        datas = {'active_ids': self.env.context.get('active_ids', []),
                 'form': self.read(['date_start', 'date_end'])[0]}
        datas['form']['company_id'] = [self.company_id.id, self.company_id.name]
        values = self.env.ref('pragtech_dental_management.patient_by_procedure_qweb').report_action(self, data=datas)
        return values
