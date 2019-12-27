# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError
from odoo.tools import email_split, float_is_zero
import time
from odoo.exceptions import UserError, AccessError, ValidationError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def get_staff_commission_ins(self, employee, start_datetime, end_datetime):
        employee = self.env['hr.employee'].browse(employee)
        staff_commission_total = 0.0
        if not employee.user_id:
            raise UserError('No Internal user defined for Employee %s' % employee.name)
        doctor = self.env['medical.physician'].search([('name.user_id', '=', employee.user_id.id)])
        if not doctor:
            raise UserError('No Doctor created for Employee %s' % employee.name)
        dom = [('date_invoice', '>=', start_datetime),
               ('date_invoice', '<=', end_datetime),
               ('is_patient', '=', True),
               ('type', '=', 'out_invoice'),
               ('dentist', '=', doctor.id),
               ('state', 'in', ['open', 'paid'])]
        invoice_ids = self.env['account.invoice'].search(dom)
        res = []
        for each_record in invoice_ids:
            income_sale_price = 0.0
            material_cost = 0.0
            for line in each_record.invoice_line_ids:
                income_sale_price += line.price_subtotal
                for consumable in line.product_id.consumable_ids:
                    x = (consumable.consu_product_id.lst_price * consumable.quantity) * line.quantity
                    material_cost += x
            if not each_record.dentist.target_amount:
                raise UserError('No Target amount set for Doctor %s' % each_record.dentist.name.name)
            if not each_record.dentist.commission:
                raise UserError('No Commission set for Doctor %s' % each_record.dentist.name.name)
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
        for record in res:
            hike = 0.0
            record['Hike'] = 0.0
            if record['Profit'] > record['target_amount']:
                hike = ((record['Profit'] - record['target_amount']) * record['commission']) / 100
                record['Hike'] = hike
                staff_commission_total = record['Hike']
        return staff_commission_total


