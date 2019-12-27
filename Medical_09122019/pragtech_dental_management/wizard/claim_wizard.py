from odoo import models, fields, api, _
import base64
from odoo.tools.misc import xlwt
import io
from odoo.exceptions import UserError
from datetime import datetime


class ClaimWizard(models.TransientModel):
    _name = 'dental.claim.wizard'
    
    company = fields.Many2one('res.partner',string='Insurance Company',domain="[('is_insurance_company', '=', True)]",
                              required=True)
    to_date = fields.Date(string='To Date')
    from_date = fields.Date(string='From Date')
    data = fields.Binary('File', readonly=True)
    state = fields.Selection([('choose', 'choose'),   # choose language
                                       ('get', 'get')], default='choose')  
    name = fields.Char('File Name', readonly=True)
    @api.multi
    def print_report(self):
        datas = {'active_ids': self.env.context.get('active_ids', []),
                 'form':self.read(['to_date', 'from_date'])[0],
                 }
        values=self.env.ref('pragtech_dental_management.claim_report_qweb').report_action(self, data=datas)
        return values
    
    
    @api.multi  
    def generate_backlog_excel_report(self):
        if not self.company.insur_report_format:
            raise UserError(_("Assign Report format for this Insurance Company"))
        if self.company.insur_report_format == 'qlm':
            workbook = xlwt.Workbook(encoding='utf-8')
            worksheet = workbook.add_sheet('Claim Report')
            # Add a font format to use to highlight cells.
            #         bold = workbook.add_format({'bold':True,'size': 10})
            #         normal = workbook.add_format({'size': 10})
            #          workbook = xlsxwriter.Workbook('/tmp/abc.xlsx')
            #         ('/tmp/%s.xlsx'%self.from_date)
            #         worksheet = workbook.add_worksheet()

            bold = xlwt.easyxf("font: bold on;")
            normal = xlwt.easyxf()
            r = 0
            c = 0

            data_list = []
            output_header = ['Patient Name', 'MEM ID', 'Date of Birth', 'Nationality', 'Country of Residence', 'Sex',
                             'Mobile', 'Invoice Number',
                             'Healthcare Professional', 'Healthcare Professional ID', 'Healthcare Professional Type',
                             'Episode Number', 'Doctor', 'Appointment Start',
                             'Appointment End', 'State', 'Treatment', 'Treatment Code', 'Treatment price',
                             'Treatment group discount(%)', 'Co-payment', 'Amount paid by patient']
            for item in output_header:
                worksheet.write(r, c, item, bold)
                c += 1

            inv_data = self.env['account.invoice'].search \
                ([('date_invoice', '>=', self.from_date), ('date_invoice', '<=', self.to_date),
                  ('patient', '!=', False)])
            #         data = []
            for inv in inv_data:
                if inv.patient.apt_id and inv.insurance_company == self.company:
                    for apt in inv.patient.apt_id:
                        data = []
                        data.append(inv.patient.name.name)
                        if inv.patient.name.ref:
                            data.append(inv.patient.name.ref)
                        else:
                            data.append('')
                        if inv.patient.dob:
                            data.append(inv.patient.dob)
                        else:
                            data.append('')
                        if inv.patient.nationality_id:
                            data.append(inv.patient.nationality_id.name)
                        else:
                            data.append('')
                        if inv.patient.name.country_id:
                            data.append(inv.patient.name.country_id.name)
                        else:
                            data.append('')
                        if inv.patient.sex:
                            if inv.patient.sex == 'm':
                                data.append('Male')
                            else:
                                data.append('Female')
                        else:
                            data.append('')
                        if inv.patient.mobile:
                            data.append(inv.patient.mobile)
                        else:
                            data.append('')
                        if inv.number:
                            data.append(inv.number)
                        else:
                            data.append('')
                        if inv.dentist:
                            data.append(inv.dentist.name.name)
                        else:
                            data.append('')
                        if inv.dentist.code:
                            data.append(inv.dentist.code)
                        else:
                            data.append('')
                        if inv.dentist.speciality:
                            data.append(inv.dentist.speciality.name)
                        else:
                            data.append('')
                        if apt:
                            data.append(apt.name)
                            if apt.doctor:
                                data.append(apt.doctor.name.name)
                            else:
                                data.append(' ')
                            if apt.appointment_sdate:
                                data.append(apt.appointment_sdate)
                            else:
                                data.append(' ')
                            if apt.appointment_edate:
                                data.append(apt.appointment_edate)
                            else:
                                data.append(' ')
                            if apt.state:
                                data.append(apt.state)
                            else:
                                data.append('')
                        else:
                            data.append('')
                            data.append('')
                            data.append('')
                            data.append('')
                            data.append('')
                        if inv.invoice_line_ids:
                            product = []
                            p_code = []
                            for line in inv.invoice_line_ids:
                                product.append(line.product_id.name)
                                if line.product_id.default_code:
                                    p_code.append(str(line.product_id.default_code))
                                else:
                                    p_code.append('')

                                data.append(line.product_id.name or '')
                                data.append(line.product_id.default_code or '')
                                data.append(line.price_unit)
                                data.append(line.discount_amt)
                                data.append(line.amt_paid_by_patient)
                                data.append(line.price_subtotal)

                            if product:
                                product = ','.join(product)
                            else:
                                product = ''
                            if p_code:
                                p_code = ','.join(p_code)
                            else:
                                p_code = ''
                                #                         data.append(product)
                                #                         data.append(p_code)

                        else:
                            data.append('')

                        data_list.append(data)

                        #         print("\n\n\n\n\n",data)
                        #         data_list = [['1','2'],['1','GFHC'],['22','adygb']]
            r += 1
            for data in data_list:
                c = 0
                for item in data:
                    worksheet.write(r, c, item, normal)
                    c += 1
                r += 1

            buf = io.BytesIO()
            workbook.save(buf)
            out = base64.encodestring(buf.getvalue())
            name = "claim_report.xls"
            self.write({'state': 'get', 'data': out, 'name': name})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'dental.claim.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }
        if self.company.insur_report_format == 'nextcare_allianz':
            workbook = xlwt.Workbook(encoding='utf-8')
            worksheet = workbook.add_sheet('Claim Report')
            bold = xlwt.easyxf("font: bold on;")
            r = 0
            c = 3
            output_header = ['INSURANCE CLAIM SHEET']
            for item in output_header:
                worksheet.write(r, c, item, bold)
            r += 2
            c = 0
            from_date = (datetime.strptime(self.from_date, '%Y-%m-%d'))
            from_date = from_date.strftime('%m/%d/%Y %H:%M:%S').split(' ')[0]
            to_date = (datetime.strptime(self.to_date, '%Y-%m-%d'))
            to_date = to_date.strftime('%m/%d/%Y %H:%M:%S').split(' ')[0]
            output_header = ['Period From:', from_date, 'Period To:', to_date]
            for item in output_header:
                worksheet.write(r, c, item, bold)
                c += 2
            r += 1
            c = 0
            output_header = ['Insurance Company:', self.company.name,
                             'Report Date:',datetime.now().strftime('%m/%d/%Y %H:%M:%S')]
            for item in output_header:
                worksheet.write(r, c, item, bold)
                c += 2
            normal = xlwt.easyxf()
            r += 2
            c = 0
            data_list = []
            Amt_company = 'Amount(' + self.company.name + ')'
            output_header = ['SN', 'TRT DATE', 'FILE NO.', 'INV. NO.', 'Policy Number', 'Patient Name',
                             'Service Code', 'Service Description',
                             'GROSS', 'Discount (00%)', 'NET',
                             'Paid by Member', Amt_company, 'Approval Code', 'Approved amount', 'Insurance total']
            for item in output_header:
                worksheet.write(r, c, item, bold)
                c += 1
            inv_data = self.env['account.invoice'].search \
                ([('date_invoice', '>=', self.from_date), ('date_invoice', '<=', self.to_date),
                  ('patient', '!=', False), ('insurance_company', '=', self.company.id),
                  ('state', 'in', ('open', 'paid'))])
            sl_no = 0
            for inv in inv_data:
                for line in inv.invoice_line_ids:
                    if line.apply_insurance:
                        data = []
                        sl_no += 1
                        data.append(sl_no)
                        date_inv = ''
                        if inv.date_invoice:
                            date_inv = (datetime.strptime(inv.date_invoice, '%Y-%m-%d'))
                            date_inv = date_inv.strftime('%m/%d/%Y %H:%M:%S').split(' ')[0]
                        data.append(date_inv)
                        data.append(inv.patient.patient_id)
                        data.append(inv.number)
                        data.append(inv.insurance_card.number)
                        data.append(inv.patient.name.name)
                        data.append(line.product_id.default_code or '')
                        data.append(line.product_id.name or '')
                        gross = line.quantity * line.price_unit
                        data.append(gross)
                        data.append(line.discount_amt)


                        ins_total = 0
                        treatment_total = 0
                        if inv.insurance_company.insurance_cases == 'case_1':
                            treatment_total += (line.price_unit * line.quantity * line.discount_amt) / 100
                            ins_total += (line.price_unit * line.quantity * line.amt_paid_by_insurance) / 100
                        if inv.insurance_company.insurance_cases in ('case_3', 'case_2'):
                            treatment_total += (line.price_unit * line.quantity * line.discount_amt) / 100
                            total_payable = line.price_unit * line.quantity - treatment_total
                            ins_total += (total_payable * line.amt_paid_by_insurance) / 100
                        data.append(gross - treatment_total)
                        data.append(line.price_initial_copay)
                        data.append(ins_total)
                        data.append(inv.ins_approval_code)
                        data.append(inv.ins_approved_amt)
                        data.append(inv.insurance_total)
                        data_list.append(data)
            r += 1
            for data in data_list:
                c = 0
                for item in data:
                    worksheet.write(r, c, item, normal)
                    c += 1
                r += 1
            buf = io.BytesIO()
            workbook.save(buf)
            out = base64.encodestring(buf.getvalue())
            name = "claim_report.xls"
            self.write({'state': 'get', 'data': out, 'name': name})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'dental.claim.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }


        