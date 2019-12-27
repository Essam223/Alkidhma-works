from odoo import models,fields,api


class CostProfitWizard(models.TransientModel):
    _name = 'cost.profit.wizard'
    _description = 'Cost Profit Wizard'
    
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
    date_start = fields.Date('From Date', required=True, default=fields.Date.context_today)
    date_end = fields.Date('To Date', required=True, default=fields.Date.context_today)
    treatment_id = fields.Many2one('product.product', 'Treatment', domain=[('is_treatment', '=', True)])
    doctor = fields.Many2one('medical.physician', "Doctor", domain=_get_doctor_id)

    @api.model
    def default_get(self, fields):
        res = super(CostProfitWizard, self).default_get(fields)
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
    def print_report(self):
        doctor = False
        treatment_id = False
        if self.treatment_id:
            treatment_id = [self.treatment_id.id, self.treatment_id.name]
        if self.doctor:
            doctor = [self.doctor.id, self.doctor.name.name]
        datas = {'active_ids': self.env.context.get('active_ids', []),
                 'form': self.read(['date_start', 'date_end'])[0],
                 'doctor': doctor,
                 'treatment_id': treatment_id,
                 }
        values = self.env.ref('staffcommission_mdc.cost_profit_qweb').report_action(self, data=datas)
        return values
