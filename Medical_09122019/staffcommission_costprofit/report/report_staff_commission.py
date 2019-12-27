from odoo import api, fields, models, SUPERUSER_ID,_
import base64
from odoo.exceptions import Warning, UserError
from datetime import datetime
import time


class ReportStaffCommission(models.AbstractModel):
    _name = 'report.staffcommission_costprofit.staff_commission_report_pdf'

    @api.model
    def get_staffcommission(self, start_date=False, end_date=False, doctor=False):
        dom = [('date_invoice', '>=', start_date),
               ('date_invoice', '<=', end_date),
               ('is_patient', '=', True),
               ('dentist', '!=', False),
               ('type', '=', 'out_invoice'),
               ('state', 'in', ['open', 'paid'])]
        if doctor:
            dom.append(('dentist', '=', doctor[0]))
        invoice_ids = self.env['account.invoice'].search(dom)
        res = []
        for each_record in invoice_ids:
            if not each_record.dentist.name.user_id:
                raise UserError('No Internal user defined for Doctor %s' % each_record.dentist.name.name)
            employee = self.env['hr.employee'].search([('user_id', '=', each_record.dentist.name.user_id.id)])
            if not employee:
                raise UserError('No Employee created for Doctor %s' % each_record.dentist.name.name)
            if not each_record.dentist.target_amount:
                raise UserError('No Target amount set for Doctor %s' % each_record.dentist.name.name)
            if not each_record.dentist.commission:
                raise UserError('No Commission set for Doctor %s' % each_record.dentist.name.name)
            income_sale_price = 0.0
            material_cost = 0.0
            for line in each_record.invoice_line_ids:
                income_sale_price += line.price_subtotal
                for consumable in line.product_id.consumable_ids:
                    x = (consumable.consu_product_id.lst_price * consumable.quantity) * line.quantity
                    material_cost += x
            if not res:
                res.append({'dentist_id': each_record.dentist.id,
                            'dentist_name': each_record.dentist.name.name,
                            'target_amount': each_record.dentist.target_amount,
                            'commission': each_record.dentist.commission,
                            'income_sale_price': income_sale_price,
                            'Material_cost': material_cost,
                            'Profit': income_sale_price - material_cost,
                            'customer_count': 1})
            else:
                flag = 0
                for each_res in res:
                    if each_record.dentist.id == each_res['dentist_id']:
                        each_res['customer_count'] += 1
                        each_res['income_sale_price'] += income_sale_price
                        each_res['Material_cost'] += material_cost
                        profit = income_sale_price - material_cost
                        each_res['Profit'] += profit
                        flag = 1
                        break
                if flag == 0:
                    res.append({'dentist_id': each_record.dentist.id,
                                'dentist_name': each_record.dentist.name.name,
                                'target_amount': each_record.dentist.target_amount,
                                'commission': each_record.dentist.commission,
                                'income_sale_price': income_sale_price,
                                'Material_cost': material_cost,
                                'Profit': income_sale_price - material_cost,
                                'customer_count': 1})
        for record in res:
            hike = 0.0
            record['Hike'] = 0.0
            if record['Profit'] > record['target_amount']:
                hike = ((record['Profit'] - record['target_amount']) * record['commission']) / 100
                record['Hike'] = hike
        return res

    @api.multi
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        start_date = data['form']['date_start']
        end_date = data['form']['date_end']
        doctor = data['doctor']
        final_records = self.get_staffcommission(start_date, end_date, doctor)
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
            'get_staffcommission': final_records,
            'doctor': doctor,
        }
        # data['period_start'] = datetime.strptime(data['period_start'], '%Y-%m-%d')
        # data['period_stop'] = datetime.strptime(data['period_stop'], '%Y-%m-%d')
        # return data
