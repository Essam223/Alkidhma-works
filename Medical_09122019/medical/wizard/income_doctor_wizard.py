# -*- coding: utf-8 -*-
from odoo import fields, models, api


class IncomeByNurseReportWizard(models.TransientModel):
    _name = 'income.by.nurse'
   
    start_date = fields.Date('Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date('End Date', required=True, default=fields.Date.context_today)
    
    @api.multi
    def income_by_nurse_report(self):
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        return self.env.ref('medical.action_report_income_by_nurse').report_action(self, data=data)