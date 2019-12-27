from odoo import api, fields, models, _
from odoo.exceptions import UserError
import json
from odoo.addons import decimal_precision as dp

TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Vendor Bill
    'out_refund': 'out_invoice',        # Customer Credit Note
    'in_refund': 'in_invoice',          # Vendor Credit Note
}


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def invoice_print(self):
        self.ensure_one()
        self.sent = True
        if self.is_patient:
            return self.env.ref('pragtech_dental_management.report_patient_invoice_pdf').report_action(self)
        else:
            return self.env.ref('account.account_invoices').report_action(self)

    @api.multi
    def action_invoice_open_new(self):
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
            raise UserError(_("Invoice must be in draft state in order to validate it."))
        if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
            raise UserError(_(
                "You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        to_open_invoices.invoice_validate_new()

    @api.multi
    def invoice_validate_new(self):
        self.patient_invoice_validate()
        for invoice in self.filtered(lambda invoice: invoice.partner_id not in invoice.message_partner_ids):
            invoice.message_subscribe([invoice.partner_id.id])
        self._check_duplicate_supplier_reference()
        self.write({'state': 'open'})

    def action_invoice_Register_Payment(self):
        self.action_invoice_open_new()
        action = self.env.ref('account.action_account_invoice_payment').read()[0]
        return action

    patient = fields.Many2one("medical.patient", 'Patient', readonly=True)
    dentist = fields.Many2one('medical.physician', 'Doctor')
    insurance_card = fields.Many2one('medical.insurance', 'Insurance Card', domain="[('patient_id', '=', patient)]",
                                     readonly=True, states={'draft': [('readonly', False)]}, track_visibility='always')
    insurance_company = fields.Many2one('res.partner', 'Insurance Company', track_visibility='always')
    insurance_company_domain = fields.Char('Domain', compute='_get_ins_company_domain', store=True)
    insurance_total = fields.Monetary(string='Insurance Total', store=True, readonly=True,
                                      compute='_compute_insurance_total',
                                      track_visibility='always')
    treatment_group_disc_total = fields.Monetary(string='Ins.Discount', store=True, readonly=True,
                                                 compute='_compute_insurance_total',
                                                 track_visibility='always')
    patient_copayment_total = fields.Monetary(string='Co-payment', store=True, readonly=True,
                                              compute='_compute_insurance_total',
                                              track_visibility='always')
    is_consultation = fields.Boolean(string='is consultation', store=True, readonly=True,
                                     compute='_compute_insurance_total',
                                     track_visibility='always')
    is_treatment = fields.Boolean(string='is treatment', store=True, readonly=True,
                                  compute='_compute_insurance_total',
                                  track_visibility='always')
    initial_patient_copayment = fields.Monetary(string='Initial Co-payment', store=True, readonly=True,
                                                compute='_compute_insurance_total',
                                                track_visibility='always')
    consultation_net_amt = fields.Monetary(string='Consultation Patient-company amt', store=True, readonly=True,
                                           compute='_compute_insurance_total',
                                           track_visibility='always')
    net_amount = fields.Monetary(string='Net Amt', store=True, readonly=True,
                                 compute='_compute_insurance_total',
                                 track_visibility='always')
    amount_subtotal = fields.Monetary(string='Gross Amt', store=True, readonly=True,
                                      compute='_compute_subtotall',
                                      track_visibility='always')
    initial_insurance = fields.Monetary(string='Initial Insurance Total', store=True, readonly=True,
                                        compute='_compute_insurance_total',
                                        track_visibility='always')
    ins_approved_amt = fields.Monetary(string='Treatment Approved amount', track_visibility='always',
                                       readonly=True, states={'draft': [('readonly', False)]})
    consult_approved_amt = fields.Monetary(string='Consultation Approved amount', track_visibility='always',
                                           readonly=True, states={'draft': [('readonly', False)]})

    @api.depends('invoice_line_ids', 'invoice_line_ids.price_subtotal', 'invoice_line_ids.amt_paid_by_insurance',
                 'ins_approved_amt', 'consult_approved_amt')
    def _compute_insurance_total(self):
        for record in self:
            record.insurance_total = 0.0
            record.treatment_group_disc_total = 0.0
            record.patient_copayment_total = 0.0
            record.is_treatment = False
            record.is_consultation = False
            record.initial_patient_copayment = 0.0
            record.consultation_net_amt = 0.0
            record.net_amount = 0.0
            record.initial_insurance = 0.0

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'currency_id', 'company_id',
                 'date_invoice', 'type', 'invoice_line_ids.quantity', 'invoice_line_ids.price_unit')
    def _compute_subtotall(self):
        self.amount_subtotal = sum(line.price_unit * line.quantity for line in self.invoice_line_ids)

    @api.multi
    @api.onchange('partner_id')
    def partner_onchange(self):
        if (self.partner_id and self.partner_id.is_patient):
            patient_id = self.env['medical.patient'].search([('name', '=', self.partner_id.id)])
            self.patient = patient_id.id
        else:
            self.patient = False

    @api.one
    @api.depends('partner_id', 'insurance_company')
    def _get_ins_company_domain(self):
        if self.partner_id.is_patient:
            domain_list = [insurance.company_id.id for insurance in self.partner_id.insurance_ids]
            self.insurance_company_domain = json.dumps([('id', 'in', domain_list)])
        else:
            self.insurance_company_domain = json.dumps([('id', 'in', [])])

    @api.model
    def create(self, vals):
        company_id = vals.get('company_id')
        partner_id = vals.get('partner_id')
        account_id = vals.get('account_id')
        if company_id and partner_id:
            partner_brw = self.env['res.partner'].browse(partner_id)
            account_id = self.env['account.account'].browse(account_id)
            if partner_brw.property_account_receivable_id.company_id.id != company_id or \
                            account_id.company_id.id != company_id:
                company_browse = self.env['res.company'].browse(company_id)
                receiv_val_ref, payable_val_ref = company_browse.get_account_receiv_payable(company_id)
                partner_brw.write({'property_account_receivable_id':int(receiv_val_ref),
                                   'property_account_payable_id': int(payable_val_ref)})
                vals['account_id'] = int(receiv_val_ref)
        res = super(AccountInvoice, self).create(vals)
        patient_id = self.env['medical.patient'].search([('name', '=', res.partner_id.id)])
        if patient_id:
            res.patient = patient_id.id
        else:
            res.patient = False
        return res

    @api.multi
    @api.onchange('partner_id')
    def check_patient_invoice(self):
        for rec in self:
            if rec.partner_id:
                rec.is_insurance_company = rec.partner_id.is_insurance_company
                patient_ids = self.env['medical.patient'].search([('name', '=', rec.partner_id.id)])
                if not rec.patient and patient_ids:
                    rec.patient = patient_ids.ids[0]
                    rec.is_patient = True
            else:
                rec.is_patient = False
                rec.is_insurance_company = False
                rec.patient = False

    is_patient = fields.Boolean("Is Patient?", readonly=True)
    is_insurance_company = fields.Boolean("Is Insurance Invoice?", readonly=True)
    insurance_invoice = fields.Many2one("account.invoice", 'Insurance invoice', readonly=True, copy=False)
    appt_id = fields.Many2one("medical.appointment", 'Appointment', readonly=True)
    event_reference_code = fields.Char(string='Event reference Code', track_visibility='always',
                                       readonly=True, states={'draft': [('readonly', False)]})
    pre_approval_code = fields.Char(string='Pre-approval Code', track_visibility='always',
                                       readonly=True, states={'draft': [('readonly', False)]})
    ins_approval_code = fields.Char(string='Approval Code', track_visibility='always',
                                       readonly=True, states={'draft': [('readonly', False)]})

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        """ Prepare the dict of values to create the new credit note from the invoice.
            This method may be overridden to implement custom
            credit note generation (making sure to call super() to establish
            a clean extension chain).

            :param record invoice: invoice as credit note
            :param string date_invoice: credit note creation date from the wizard
            :param integer date: force date from the wizard
            :param string description: description of the credit note from the wizard
            :param integer journal_id: account.journal from the wizard
            :return: dict of value to create() the credit note
        """
        values = {}
        for field in self._get_refund_copy_fields():
            if invoice._fields[field].type == 'many2one':
                values[field] = invoice[field].id
            else:
                values[field] = invoice[field] or False

        values['invoice_line_ids'] = self._refund_cleanup_lines(invoice.invoice_line_ids)
        tax_lines = invoice.tax_line_ids
        values['tax_line_ids'] = self._refund_cleanup_lines(tax_lines)

        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
        elif invoice['type'] == 'in_invoice':
            journal = self.env['account.journal'].search([('type', '=', 'purchase'), ('company_id', '=', self.company_id.id)], limit=1)
        else:
            journal = self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', self.company_id.id)], limit=1)
        values['journal_id'] = journal.id

        values['type'] = TYPE2REFUND[invoice['type']]
        values['date_invoice'] = date_invoice or fields.Date.context_today(invoice)
        values['state'] = 'draft'
        values['number'] = False
        values['origin'] = invoice.number
        values['is_patient'] = invoice.is_patient
        values['appt_id'] = invoice.appt_id.id if invoice.appt_id else False
        values['patient'] = invoice.patient.id if invoice.patient else False
        values['dentist'] = invoice.dentist.id if invoice.dentist else False
        values['insurance_company'] = invoice.insurance_company.id if invoice.insurance_company else False
        values['insurance_card'] = invoice.insurance_card.id if invoice.insurance_card else False
        values['refund_invoice_id'] = invoice.id

        if date:
            values['date'] = date
        if description:
            values['name'] = description
        return values

    def patient_invoice_validate(self):
        pass

    @api.multi
    def invoice_validate(self):
        self.patient_invoice_validate()
        return super(AccountInvoice, self).invoice_validate()

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        if self:
            related_appt = self.env['medical.appointment'].search([('invoice_id', '=', self.id)])
            if related_appt:
                if self.state in ('open', 'paid'):
                    related_appt.write({'state': 'visit_closed'})
            if related_appt:
                if self.state not in ('open', 'paid'):
                    related_appt.write({'state': 'done'})
        self.appt_id.write({'insurance_id': self.insurance_card.id})
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    quantity = fields.Float(string='Quantity', digits=dp.get_precision('Discount'),
                            required=True, default=1)
    amt_paid_by_patient = fields.Float('Co-payment(%)', default=100)
    amt_fixed_paid_by_patient = fields.Float('Co-payment')
    amt_paid_by_insurance = fields.Float('By Insurance Company(%)', compute='onchange_amt')
    discount_amt = fields.Float('Treatment Group Discount(%)')
    apply_insurance = fields.Boolean('Apply Insurance?', compute='_apply_insurance', store=True)
    insurance_cases = fields.Selection([('case_1', 'Case 1'),('case_2', 'Case 2'), ('case_3', 'Case 3')], 'Insurance Type')
    insurance_company = fields.Many2one('res.partner', 'Insurance Company',related='invoice_id.insurance_company')
    price_initial_copay = fields.Monetary(string='Initial Copay',
                                          store=True, readonly=True, compute='_compute_price',
                                          help="Initial copay")

    @api.onchange('amt_paid_by_patient', 'discount_amt')
    @api.depends('amt_paid_by_patient', 'discount_amt')
    def onchange_amt(self):
        for this in self:
            if this.apply_insurance:
                this.amt_paid_by_insurance = 0.0

    @api.one
    @api.depends('amt_paid_by_patient', 'amt_paid_by_insurance', 'discount_amt', 'invoice_id.insurance_company',
                 'price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'invoice_id.date', 'discount_fixed_percent', 'discount',
                 'discount_value')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                          partner=self.invoice_id.partner_id)
        self_price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        if not self.discount_fixed_percent:
            self_price_subtotal = self_price_subtotal
        if self.discount_fixed_percent == 'Percent':
            self_price_subtotal = self_price_subtotal * (1 - (self.discount or 0.0) / 100.0)
        if self.discount_fixed_percent == 'Fixed':
            self_price_subtotal = self_price_subtotal - self.discount_value
        self.price_subtotal = self_price_subtotal
        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(
                price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
        self.price_initial_copay = 0.0

    @api.one
    @api.depends('invoice_id.partner_id', 'invoice_id.insurance_company', 'product_id')
    def _apply_insurance(self):
        if self.invoice_id.insurance_company:
            treatment_companies = [ins_company.id for ins_company in self.product_id.insurance_company_ids]
            patient_companies = [insurance.company_id.id for insurance in self.partner_id.insurance_ids]
            self.apply_insurance = True if self.invoice_id.insurance_company.id in patient_companies and self.invoice_id.insurance_company.id in treatment_companies else False
        else:
            self.apply_insurance = False

