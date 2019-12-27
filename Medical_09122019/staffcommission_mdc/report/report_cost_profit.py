# -*- coding: utf-8 -*-
import time
from odoo import api, models, _
from odoo.exceptions import UserError
from datetime import datetime


class ReportCostProfit(models.AbstractModel):

    _name = 'report.staffcommission_mdc.report_cost_profit'
    
    def get_cost_profit_data(self, start_date, end_date, doctor, treatment_id):
        dom = [('date_invoice', '>=', start_date),
              ('date_invoice', '<=', end_date),
              ('is_patient', '=', True),
              ('type', '=', 'out_invoice'),
              ('state', 'in', ['open', 'paid'])]
        if doctor:
            dom.append(('dentist', '=', doctor[0]))
        history_ids = self.env['account.invoice'].search(dom)
        prod_dict = {}
        for invoice in history_ids:
            income = 0.0
            overhead_amt = 0.0
            material_cost = 0.0
            if invoice:
                for line in invoice.invoice_line_ids:
                    count = 0
                    if line.product_id.is_treatment:
                        if (treatment_id and line.product_id.id == treatment_id[0]) or not treatment_id:
                            income = line.price_subtotal
                            overhead_amt = line.product_id.lst_price * (line.product_id.overhead_cost/100)
                            material_cost = 0.0
                            for consumable in line.product_id.consumable_ids:
                                material_cost += consumable.consu_product_id.lst_price * consumable.quantity
                            if line.product_id.id in prod_dict:
                                count = prod_dict[line.product_id.id][1] + line.quantity
                                prod_dict[line.product_id.id][1] = count
                                overhead_final = overhead_amt * line.quantity
                                material_cost_final = material_cost * line.quantity
                                prod_dict[line.product_id.id][2] += income
                                prod_dict[line.product_id.id][3] += overhead_final
                                prod_dict[line.product_id.id][4] += material_cost_final
                                prod_dict[line.product_id.id][5] += income - material_cost_final - overhead_final
                            else:
                                overhead_final = overhead_amt * line.quantity
                                material_cost_final = material_cost * line.quantity
                                prod_dict[line.product_id.id] = [line.product_id.name, line.quantity,
                                                                 income, overhead_final, material_cost_final,
                                                                 income-material_cost_final -overhead_final]
        return [prod_dict]

    @api.multi
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        start_date = data['form']['date_start']
        end_date = data['form']['date_end']
        treatment_id = data['treatment_id']
        doctor = data['doctor']
        final_records = self.get_cost_profit_data(start_date, end_date, doctor, treatment_id)
        period_start = datetime.strptime(start_date, '%Y-%m-%d')
        period_stop = datetime.strptime(end_date, '%Y-%m-%d')
        return {
            'period_start': period_start,
            'period_stop': period_stop,
            'doc_ids': self.ids,
            'doc_model': 'cost.profit.wizard',
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_cost_profit_data': final_records,
            'treatment_id': treatment_id,
            'doctor': doctor,
        }
    
    def formatLang(self, value, digits=None, date=False, date_time=False, grouping=True, monetary=False, dp=False,
                   currency_obj=False, lang=False):
        if lang:
            self.env.context['lang'] = lang
        return super(ReportCostProfit, self).formatLang(value, digits=digits, date=date, date_time=date_time,
                                                               grouping=grouping, monetary=monetary, dp=dp,
                                                               currency_obj=currency_obj)
