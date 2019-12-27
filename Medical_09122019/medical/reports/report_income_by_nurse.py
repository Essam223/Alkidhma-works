# -*- coding: utf-8 -*-
import time
from odoo import api, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class ReportIncomeByNurse(models.AbstractModel):
    _name = 'report.medical.report_income_by_nurse'

    def fetch_record(self, start_date, end_date):
        invoice_ids = self.env['account.invoice'].search([('date_invoice', '>=', start_date),
                                                          ('date_invoice', '<=', end_date),
                                                          ('nurse_id', '!=', False),
                                                          ('is_patient', '=', True),
                                                          ('state', 'in', ['open', 'paid']),
                                                          ('type', '=', 'out_invoice')])
        res = []
        for each_record in invoice_ids:
            if not res:
                res.append({'nurse_id': each_record.nurse_id.id,
                            'nurse_name': each_record.nurse_id.nurse.name,
                            'customer_count': 1,
                            'total_amount': each_record.amount_total})
            else: 
                flag = 0
                for each_res in res:
                    if each_record.nurse_id.id == each_res['nurse_id']:
                        each_res['customer_count'] += 1
                        each_res['total_amount'] += each_record.amount_total
                        flag = 1
                        break
                if flag == 0:
                    res.append({'nurse_id': each_record.nurse_id.id,
                                'nurse_name': each_record.nurse_id.nurse.name,
                                'customer_count': 1,
                                'total_amount': each_record.amount_total})
        return res

    @api.multi
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        final_records = self.fetch_record(start_date, end_date)
        period_start = datetime.strptime(start_date, '%Y-%m-%d')
        period_stop = datetime.strptime(end_date, '%Y-%m-%d')
        return {
            'period_start': period_start,
            'period_stop': period_stop,
            'doc_ids': self.ids,
            'doc_model': 'income.by.nurse',
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_income_by_nurse_info': final_records,
        }
    
    def formatLang(self, value, digits=None, date=False, date_time=False, grouping=True, monetary=False, dp=False,
                   currency_obj=False, lang=False):
        if lang:
            self.env.context['lang'] = lang
        return super(ReportIncomeByNurse, self).formatLang(value, digits=digits, date=date, date_time=date_time,
                                                            grouping=grouping, monetary=monetary, dp=dp,
                                                            currency_obj=currency_obj)


