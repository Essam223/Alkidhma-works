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
            partner_ids = [x.id for x in
                           self.env['res.partner'].search(
                               [('user_id', '=', self.env.user.id), ('is_doctor', '=', True)])]
            if partner_ids:
                doc_ids = [x.id for x in self.env['medical.physician'].search([('name', 'in', partner_ids)])]
            domain = [('id', 'in', doc_ids)]
        return domain

    is_only_doctor = fields.Boolean()
    date_start = fields.Date("Period From", required=True, default=time.strftime('%Y-%m-01'))
    date_end = fields.Date("Period To", required=True,
                              default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    doctor = fields.Many2one('medical.physician', "Doctor", domain=_get_doctor_id)

    @api.model
    def default_get(self, fields):
        res = super(StaffCommissionReportWizard, self).default_get(fields)
        res['is_only_doctor'] = False
        self._get_doctor_id()
        doc_ids = None
        group_dental_doc_menu = self.env.user.has_group('pragtech_dental_management.group_dental_doc_menu')
        group_dental_user_menu = self.env.user.has_group('pragtech_dental_management.group_dental_user_menu')
        group_dental_mng_menu = self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu')
        if group_dental_doc_menu and not group_dental_user_menu and not group_dental_mng_menu:
            res['is_only_doctor'] = True
            partner_ids = [x.id for x in
                           self.env['res.partner'].search(
                               [('user_id', '=', self.env.user.id), ('is_doctor', '=', True)])]
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
                 }
        return self.env.ref('staffcommission_costprofit.staff_commission_report').report_action(self, data=datas)
