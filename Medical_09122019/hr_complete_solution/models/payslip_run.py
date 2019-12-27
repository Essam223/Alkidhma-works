# -*- coding: utf-8 -*-
import datetime, time
from dateutil import relativedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import base64
from odoo.tools.misc import xlwt
import io


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    company_bank_acc_id = fields.Many2one('company.bank.account', string="Bank Account", copy=False, required=False,
                                          domain=lambda self: [("id", "in", self.env.user.company_id.bank_account_ids.ids)])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('close', 'Processed'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')
    data = fields.Binary('WPS Report', readonly=True)
    state_xls = fields.Selection([('choose', 'choose'),  # choose language
                              ('get', 'get')], default='choose')
    name_xls = fields.Char('File Name', readonly=True)

    @api.multi
    def compute_excel(self):
        salary_start_date = datetime.datetime.strptime(self.date_start, '%Y-%m-%d')
        payslip = self.slip_ids
        salary_year_month = str(salary_start_date.year) + str(salary_start_date.strftime('%m'))
        total_salaries = 0.0
        total_lines = 0
        for pay_slip in payslip:
            if pay_slip.employee_id.bank_account_id:
                total_lines += 1
        # total_lines = len(payslip)
        for p_slip in payslip:
            if p_slip.employee_id.bank_account_id:
                for salary in p_slip.line_ids:
                    if salary.category_id.id == self.env.ref('hr_payroll.NET').id:
                        total_salaries += salary.total
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('WPS Report')
        bold = xlwt.easyxf("font: bold on;")
        normal = xlwt.easyxf()
        r = 0
        c = 0
        data_list_1 = []
        data = []
        data.append('Employer EID')
        data.append('File Creation Date')
        data.append('File Creation Time')
        data.append('Payer EID')
        data.append('Payer QID')
        data.append('Payer Bank Short Name')
        data.append('Payer IBAN')
        data.append('Salary Year and Month')
        data.append('Total Salaries')
        data.append('Total records')
        data_list_1.append(data)
        for data in data_list_1:
            c = 0
            for item in data:
                worksheet.write(r, c, item, normal)
                c += 1
            r += 1
        data_list_2 = []
        data = []
        now = datetime.datetime.now()
        data.append(self.env.user.company_id.Employer_EID)
        data.append(str(now.year) + str(now.month) + str(now.day))
        data.append(str(now.hour) + str(now.minute))
        data.append(self.env.user.company_id.Payer_EID)
        data.append(self.env.user.company_id.Payer_QID)
        data.append(self.company_bank_acc_id.bank_code)
        data.append(self.company_bank_acc_id.iban_code)
        data.append(salary_year_month)
        data.append(total_salaries)
        data.append(total_lines)
        data_list_2.append(data)
        for data in data_list_2:
            c = 0
            for item in data:
                worksheet.write(r, c, item, normal)
                c += 1
            r += 1
        c = 0
        output_header = ['Record Sequence', 'Employee QID', 'Employee Visa ID', 'Employee Name',
                         'Employee Bank Short Name', 'Employee Account', 'Salary Frequency', 'Number of Working Days',
                         'Net Salary', 'Basic Salary', 'Extra hours', 'Extra Income', 'Deductions', 'Payment Type',
                         'Notes / Comments']
        for item in output_header:
            worksheet.write(r, c, item, bold)
            c += 1
        sl_no = 0
        data_list = []
        for line in payslip:
            if line.employee_id.bank_account_id:
                sl_no += 1
                data = []
                basic_salary = 0.0
                deduction = 0.0
                extra_income = 0.0
                net_salary = 0.0
                for salary in line.line_ids:
                    if salary.category_id.id == self.env.ref('hr_payroll.BASIC').id:
                        basic_salary += salary.total
                    if salary.category_id.id == self.env.ref('hr_payroll.DED').id:
                        deduction -= salary.total
                    if salary.category_id.id == self.env.ref('hr_payroll.ALW').id:
                        extra_income += salary.total
                    if salary.category_id.id == self.env.ref('hr_payroll.NET').id:
                        net_salary += salary.total
                salary_freq = ''
                if line.contract_id:
                    if line.contract_id.schedule_pay == 'monthly':
                        salary_freq = 'Monthly'
                    if line.contract_id.schedule_pay == 'quarterly':
                        salary_freq = 'Quarterly'
                    if line.contract_id.schedule_pay == 'semi-annually':
                        salary_freq = 'Semi-annually'
                    if line.contract_id.schedule_pay == 'annually':
                        salary_freq = 'Annually'
                    if line.contract_id.schedule_pay == 'weekly':
                        salary_freq = 'Weekly'
                    if line.contract_id.schedule_pay == 'bi-weekly':
                        salary_freq = 'Bi-weekly'
                    if line.contract_id.schedule_pay == 'bi-monthly':
                        salary_freq = 'Bi-monthly'
                total_worked_days = 0.0
                for worked_days in line.worked_days_line_ids:
                    if worked_days.code == 'WORK100':
                        total_worked_days += worked_days.number_of_days
                data.append(sl_no)
                if line.employee_id.qatar_id:
                    data.append(line.employee_id.qatar_id)
                else:
                    data.append('')
                if line.employee_id.visa_no:
                    data.append(line.employee_id.visa_no)
                else:
                    data.append('')
                data.append(line.employee_id.name)
                if line.employee_id.bank_code:
                    data.append(line.employee_id.bank_code)
                else:
                    data.append('')
                if line.employee_id.bank_account_id:
                    data.append(line.employee_id.bank_account_id.acc_number)
                else:
                    data.append('')
                data.append(salary_freq)
                data.append(total_worked_days)
                data.append(net_salary)
                data.append(basic_salary)
                data.append(0)
                data.append(extra_income)
                data.append(deduction)
                data.append('Normal payment')
                data.append('')
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
        name = "WPS_REPORT.xls"
        self.write({'state_xls': 'get', 'data': out, 'name_xls': name})

    @api.multi
    def compute_sheet_batch(self):
        self.ensure_one()
        for payslip in self.slip_ids:
            if payslip.state == 'draft':
                payslip.compute_sheet()

    @api.multi
    def action_payslip_done_batch(self):
        self.ensure_one()
        for payslip in self.slip_ids:
            if payslip.state == 'draft':
                payslip.action_payslip_done()

    @api.multi
    def close_payslip_run(self):
        self.compute_sheet_batch()
        self.action_payslip_done_batch()
        if not self.company_bank_acc_id:
            raise UserError(_('Select Bank account'))
        return self.write({'state': 'close'})

    @api.multi
    def action_payslip_cancel_batch(self):
        self.ensure_one()
        for payslip in self.slip_ids:
            if payslip.state == 'draft':
                payslip.action_payslip_cancel()

    # @api.onchange('journal_id')
    # def onchange_journal(self):
    #     for p_slip in self.slip_ids:
    #         if self.state == 'draft':
    #             p_slip.journal_id = self.journal_id.id


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.multi
    def compute_sheet(self):
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False)
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': slip_data['value'].get('contract_id'),
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': run_data.get('credit_note'),
            }
            new_payslip = self.env['hr.payslip'].create(res)
            if not new_payslip.contract_id:
                contract_ids = new_payslip.get_contract(new_payslip.employee_id, new_payslip.date_from, new_payslip.date_to)
                if contract_ids:
                    new_payslip.contract_id = self.env['hr.contract'].browse(contract_ids[0])
            payslips += new_payslip
        for payslp in payslips:
            payslp.compute_sheet()
        return {'type': 'ir.actions.act_window_close'}


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def compute_sheet(self):
        for payslip in self:
            contract_ids = payslip.contract_id.ids or payslip.get_contract(payslip.employee_id, payslip.date_from,
                                                                           payslip.date_to)
            contract_ids_list = self.env['hr.contract'].browse(contract_ids)
            payslip.worked_days_line_ids = False
            payslip.input_line_ids = False
            worked_days_line_ids = payslip.get_worked_day_lines(contract_ids_list, payslip.date_from, payslip.date_to)
            input_line_ids = payslip.get_inputs(contract_ids_list, payslip.date_from, payslip.date_to)
            payslip.worked_days_line_ids = worked_days_line_ids
            payslip.input_line_ids = input_line_ids
            payslip.onchange_employee_id(payslip.date_from, payslip.date_to, payslip.employee_id.id,
                                         payslip.contract_id)
        return super(HrPayslip, self).compute_sheet()

    department_id = fields.Many2one('hr.department', string='Department')
    contract_id_status = fields.Selection([('draft', 'New'),
                                           ('open', 'Running'),
                                           ('pending', 'To Renew'),
                                           ('close', 'Expired'),
                                           ('cancel', 'Cancelled')
                                        ], string='Contract Status', related='contract_id.state')
    net_salary = fields.Float('Net Salary', help="Employee's Net Salary.", compute='_compute_net_salary')


    @api.multi
    def onchange_employee_id(self, date_from, date_to, employee_id=False, contract_id=False):
        employee = self.env['hr.employee'].browse(employee_id)
        res =  super(HrPayslip, self).onchange_employee_id(self.date_from, self.date_to, self.employee_id.id, self.contract_id)
        res['value'].update({
            'department_id': employee.department_id.id,
        })
        return res

    def _compute_net_salary(self):
        # Contract = self.env['hr.payslip']

        for p_slip in self:
            total_salaries = 0.0
            for salary in p_slip.line_ids:
                if salary.category_id.id == self.env.ref('hr_payroll.NET').id:
                    total_salaries += salary.total
            p_slip.net_salary = total_salaries

    @api.model
    def create(self, values):
        if values.get('employee_id'):
             employee = self.env['hr.employee'].browse(values.get('employee_id'))
             if employee.department_id:
                values['department_id'] = employee.department_id.id
        res = super(HrPayslip, self).create(values)
        return res

    @api.model
    def payslip_monthly_creation(self, cron_mode=True):
        MONTH_NOW = datetime.datetime.now().strftime("%B")
        YEAR_NOW = datetime.datetime.now().year
        date_Start = time.strftime('%Y-%m-01')
        date_End = str(datetime.datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10]
        if not self.env['hr.payslip.run'].search([('date_start', '=', date_Start), ('date_end', '=', date_End)]):
            payslip_batch = self.env['hr.payslip.run'].create({
                'name': str(MONTH_NOW) + ' - ' + str(YEAR_NOW),
                'date_start': date_Start,
                'date_end': date_End,
                'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1)[0].id,
            })
            for employee in self.env['hr.employee'].search([('active', '=', True)]):
                if not self.env['hr.payslip'].search([('employee_id', '=', employee.id),
                                                      ('date_from', '=', payslip_batch.date_start),
                                                      ('date_to', '=', payslip_batch.date_end)]):
                   department_id = ""
                   if employee.department_id.id:
                        department_id = employee.department_id.id
                   self.env['hr.payslip'].create({
                        'employee_id': employee.id,
                        'department_id': department_id,
                        'contract_id': employee.contract_id.id,
                        'struct_id': employee.struct_id.id,
                        'state': 'draft',
                        'date_from': payslip_batch.date_start,
                        'date_to': payslip_batch.date_end,
                        'journal_id': payslip_batch.journal_id.id,
                        'payslip_run_id': payslip_batch.id,
                        'name': _('Salary Slip of %s for %s') % (employee.name, str(MONTH_NOW) + ' - ' + str(YEAR_NOW)),
                        'company_id': employee.company_id.id,
                    })


