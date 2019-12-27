from odoo import api, fields, models, SUPERUSER_ID,_
import base64
from odoo.exceptions import Warning, UserError
from datetime import datetime
import time


class ReportStaffCommission(models.AbstractModel):
    _name = 'report.staffcommission_mdc.staff_commission_report_pdf'

    @api.model
    def get_staffcommission(self, start_date=False, end_date=False, doctor=False, company_id=False):
        dom_patient = [('date_invoice', '>=', start_date),
               ('date_invoice', '<=', end_date),
               ('company_id', '=', company_id[0]),
               ('is_patient', '=', True),
               ('dentist', '!=', False),
               ('type', '=', 'out_invoice'),
               ('state', 'in', ['open', 'paid'])]
        if doctor:
            dom_patient.append(('dentist', '=', doctor[0]))
        patient_invoice_ids = self.env['account.invoice'].search(dom_patient)
        res = []
        for each_record in patient_invoice_ids:
            if not each_record.dentist.name.user_id:
                raise UserError('No Internal user defined for Doctor %s' % each_record.dentist.name.name)
            employee = self.env['hr.employee'].search([('user_id', '=', each_record.dentist.name.user_id.id)])
            if not employee:
                raise UserError('No Employee created for Doctor %s' % each_record.dentist.name.name)
            if not each_record.dentist.commission_ids:
                raise UserError('No Commission set for Doctor %s' % each_record.dentist.name.name)
            income_sale_price = 0.0
            material_cost = 0.0
            for line in each_record.invoice_line_ids:
                income_sale_price += line.price_subtotal
                # for consumable in line.product_id.consumable_ids:
                #     x = (consumable.consu_product_id.lst_price * consumable.quantity) * line.quantity
                #     material_cost += x
            if not res:
                res.append({'dentist_id': each_record.dentist.id,
                            'dentist_name': each_record.dentist.name.name,
                            # 'target_amount': each_record.dentist.target_amount,
                            # 'commission': each_record.dentist.commission,
                            'income_sale_price': income_sale_price,
                            'Material_cost': material_cost,
                            'profit': income_sale_price - material_cost,
                            'customer_count': 1})
            else:
                flag = 0
                for each_res in res:
                    if each_record.dentist.id == each_res['dentist_id']:
                        each_res['customer_count'] += 1
                        each_res['income_sale_price'] += income_sale_price
                        each_res['Material_cost'] += material_cost
                        profit = income_sale_price - material_cost
                        each_res['profit'] += profit
                        flag = 1
                        break
                if flag == 0:
                    res.append({'dentist_id': each_record.dentist.id,
                                'dentist_name': each_record.dentist.name.name,
                                # 'target_amount': each_record.dentist.target_amount,
                                # 'commission': each_record.dentist.commission,
                                'income_sale_price': income_sale_price,
                                'Material_cost': material_cost,
                                'profit': income_sale_price - material_cost,
                                'customer_count': 1})
        for record in res:
            dom_lab = [('date_invoice', '>=', start_date),
                       ('date_invoice', '<=', end_date),
                       ('company_id', '=', company_id[0]),
                       ('is_laboratory', '=', True),
                       ('dentist', '=', record['dentist_id']),
                       ('type', '=', 'in_invoice'),
                       ('state', 'in', ['open', 'paid'])]
            lab_bill_ids = self.env['account.invoice'].search(dom_lab)
            lab_cost = sum(lab_bill.amount_total for lab_bill in lab_bill_ids)
            record['lab_cost'] = lab_cost
            record['profit'] -= lab_cost
            dom_refund = [('date_invoice', '>=', start_date),
                         ('date_invoice', '<=', end_date),
                         ('company_id', '=', company_id[0]),
                         ('is_patient', '=', True),
                         ('dentist', '=', record['dentist_id']),
                         ('type', '=', 'out_refund'),
                         ('state', 'in', ['open', 'paid'])]
            refund_bill_ids = self.env['account.invoice'].search(dom_refund)
            refund_cost = sum(refund_bill.amount_total for refund_bill in refund_bill_ids)
            record['refund_cost'] = refund_cost
            record['profit'] -= refund_cost
            doctor_rec = self.env['medical.physician'].browse(record['dentist_id'])
            list_commision = []
            for commission in doctor_rec.commission_ids:
                commission_calc_amt = 0.0
                commission_final = 0.0
                from_amt = commission.from_amt
                to_amt = commission.to_amt
                commission_perc = commission.commission
                c_between = from_amt <= record['profit'] <= to_amt
                c_last = from_amt <= record['profit'] and not to_amt
                if c_between:
                    commission_calc_amt = record['profit'] - from_amt
                    calculated_comm = (commission_calc_amt * commission_perc) / 100
                    if calculated_comm > 0:
                        commission_final = calculated_comm
                if c_last:
                    commission_calc_amt = record['profit'] - from_amt
                    calculated_comm = (commission_calc_amt * commission_perc) / 100
                    if calculated_comm > 0:
                        commission_final = calculated_comm
                if not c_between and not c_last and from_amt<= record['profit']:
                    commission_calc_amt = to_amt - from_amt
                    calculated_comm = (commission_calc_amt * commission_perc) / 100
                    if calculated_comm > 0:
                        commission_final = calculated_comm
                list_commision.append({'from_amt': from_amt,
                                      'to_amt': to_amt,
                                      'commission': commission_perc,
                                      'commission_calc_amt': commission_calc_amt,
                                      'commission_final': commission_final,
                                       })
            record['list_commision'] = list_commision
            commission_dr_percent = 0.0
            record['commission_dr_percent'] = 0.0
            if record['profit']:
                for list_comm in record['list_commision']:
                    commission_dr_percent += list_comm['commission_final']
                record['commission_dr_percent'] = commission_dr_percent
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
        company_id = data['company_id']
        final_records = self.get_staffcommission(start_date, end_date, doctor, company_id)
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
            'company_id': company_id,
            'doctor': doctor,
        }
