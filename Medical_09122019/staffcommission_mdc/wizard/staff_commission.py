from odoo import models,fields,api, SUPERUSER_ID
import time
from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta


class StaffCommissionReportWizard(models.TransientModel):
    _name = "staff.commission.wizard"

    def _get_doctor_id(self):
        domain = []
        doc_ids = None
        group_dental_doc_menu = self.env.user.has_group('pragtech_dental_management.group_dental_doc_menu')
        group_dental_user_menu = self.env.user.has_group('pragtech_dental_management.group_dental_user_menu')
        group_dental_mng_menu = self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu')
        if group_dental_doc_menu and not group_dental_user_menu and not group_dental_mng_menu:
            dom_partner = [('user_id', '=', self.env.user.id), ('is_doctor', '=', True),
                           ('company_id', '=', self.company_id.id)]
            partner_ids = [x.id for x in self.env['res.partner'].search(dom_partner)]
            if partner_ids:
                doc_ids = [x.id for x in self.env['medical.physician'].search([('name', 'in', partner_ids),
                                                                               ('company_id', '=', self.company_id.id)])]
        else:
            doc_ids = [x.id for x in self.env['medical.physician'].search([('company_id', '=', self.company_id.id)])]
        domain = [('id', 'in', doc_ids)]
        return domain

    is_only_doctor = fields.Boolean()
    date_start = fields.Date("Period From", required=True, default=time.strftime('%Y-%m-01'))
    date_end = fields.Date("Period To", required=True,
                              default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    doctor = fields.Many2one('medical.physician', "Doctor", domain=_get_doctor_id)

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

    @api.onchange('company_id')
    def onchange_company_id(self):
        domain = self._get_doctor_id()
        return {
            'domain': {'doctor': domain}
        }

    @api.model
    def default_get(self, fields):
        res = super(StaffCommissionReportWizard, self).default_get(fields)
        self._get_company_id()
        res['company_id'] = self.env.user.company_id.id
        res['is_only_doctor'] = False
        self._get_doctor_id()
        doc_ids = None
        group_dental_doc_menu = self.env.user.has_group('pragtech_dental_management.group_dental_doc_menu')
        group_dental_user_menu = self.env.user.has_group('pragtech_dental_management.group_dental_user_menu')
        group_dental_mng_menu = self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu')
        if group_dental_doc_menu and not group_dental_user_menu and not group_dental_mng_menu:
            res['is_only_doctor'] = True
            dom_partner = [('user_id', '=', self.env.user.id), ('is_doctor', '=', True),
                           ('company_id', '=', self.env.user.company_id.id)]
            partner_ids = [x.id for x in self.env['res.partner'].search(dom_partner)]
            if partner_ids:
                doc_ids = [x.id for x in self.env['medical.physician'].search([('name', 'in', partner_ids)])]
        if doc_ids:
            res['doctor'] = doc_ids[0]
        return res

    @api.multi
    def staffcommission_report(self):
        doctor = False
        if self.doctor:
            doctor = [self.doctor.id, self.doctor.name.name]
        datas = {'active_ids': self.env.context.get('active_ids', []),
                 'form': self.read(['date_start', 'date_end'])[0],
                 'doctor': doctor,
                 'company_id': [self.company_id.id, self.company_id.name],
                 }
        return self.env.ref('staffcommission_mdc.staff_commission_report').report_action(self, data=datas)
