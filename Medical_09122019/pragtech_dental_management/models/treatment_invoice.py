from odoo import api, fields, models, tools, _


class TreatmentInvoice(models.Model):
    _name = "treatment.invoice"

    def _get_treatment_dom_id(self):
        if self.appointment_id.insurance_id:
            doc_ids = []
            for coverage_treatmts in self.appointment_id.insurance_id.company_id.treatment_ids:
                doc_ids.append(coverage_treatmts.id)
            for non_coverage_treatmts in self.appointment_id.insurance_id.company_id.non_coverage_treatment_ids:
                doc_ids.append(non_coverage_treatmts.id)
            for consultation_treatmts in self.appointment_id.insurance_id.company_id.consultation_treatment_ids:
                doc_ids.append(consultation_treatmts.id)
            domain = [('id', 'in', doc_ids), ('is_treatment', '=', True),
                      ('company_id', '=', self.appointment_id.company_id.id)]
        else:
            domain = [('is_treatment', '=', True), ('is_clinic_treatment', '=', True),
                      ('company_id', '=', self.appointment_id.company_id.id)]
        return domain

    @api.onchange('description')
    def onchange_treatment_ids(self):
        domain = self._get_treatment_dom_id()
        return {
            'domain': {'description': domain}
        }

    def set_access_for_after_discount(self):
        for rec in self:
            if self.env['res.users'].has_group('pragtech_dental_management.group_dental_doc_menu') \
                    or self.env['res.users'].has_group('pragtech_dental_management.group_dental_mng_menu') or \
                    self.env['res.users'].has_group('account.group_account_manager'):
                rec.able_to_modify_after_discount = True

    able_to_modify_after_discount = fields.Boolean(compute=set_access_for_after_discount, string='Is user able to modify After Discount?')
    appointment_id = fields.Many2one("medical.appointment", "Appointment", required=True)
    # changes by mubaris  
    diagnosis_id = fields.Many2one('diagnosis', 'Diagnosis')
    treatment_id = fields.Many2one("medical.teeth.treatment", "Treatment")
    description = fields.Many2one('product.product', 'Treatment', required=True, domain=_get_treatment_dom_id)
    note = fields.Char("Description")
    amount = fields.Float("After Discount", required=True)
    actual_amount = fields.Float('Actual Amt', compute='_get_actual_amount')
    patient_id = fields.Many2one("medical.patient", "Patient", related='appointment_id.patient')
    date = fields.Datetime('Date', compute='_compute_date')

    @api.depends('appointment_id', 'appointment_id.appointment_sdate')
    def _compute_date(self):
        for record in self:
            if record.appointment_id:
                record.date = record.appointment_id.appointment_sdate

    @api.depends('description')
    def _get_actual_amount(self):
        for appt in self:
            if appt.description:
                appt.update({
                    'actual_amount': appt.description.lst_price
                })

    @api.onchange('treatment_id')
    def onchange_treatment_id(self):
        self.set_access_for_after_discount()
        if self.treatment_id:
            self.description = self.treatment_id.description

    @api.onchange('description')
    def onchange_description(self):
        if self.description:
            self.amount = self.description.lst_price

    @api.model
    def create(self, values):
        doc = self.env['res.users'].has_group('pragtech_dental_management.group_dental_doc_menu')
        if values.get('description') and not values.get('amount') and not doc:
            values['amount'] = self.env['product.product'].browse(values.get('description')).lst_price
        line = super(TreatmentInvoice, self).create(values)
        msg = "<b> Created New Payment Lines:</b><ul>"
        if values.get('description'):
            msg += "<li>" + _("Treatment") + ": %s<br/>" % (line.description.name)
        if values.get('note'):
            msg += "<li>" + _("Description") + ": %s  <br/>" % (line.note)
        if values.get('actual_amount'):
            msg += "<li>" + _("Actual Amt") + ": %s  <br/>" % (line.actual_amount)
        if values.get('amount'):
            msg += "<li>" + _("After Discount Amt") + ": %s  <br/>" % (line.amount)
        msg += "</ul>"
        line.appointment_id.message_post(body=msg)
        return line

    @api.multi
    def write(self, values):
        doc = self.env['res.users'].has_group('pragtech_dental_management.group_dental_doc_menu')
        if values.get('description') and not values.get('amount') and not doc:
            values['amount'] = self.env['product.product'].browse(values.get('description')).lst_price
        appoints = self.mapped('appointment_id')
        for apps in appoints:
            order_lines = self.filtered(lambda x: x.appointment_id == apps)
            msg = "<b> Updated Payment Lines :</b><ul>"
            for line in order_lines:
                if values.get('description'):
                    msg += "<li>" + _("Treatment") + ": %s -> %s <br/>" % (
                    line.description.name, self.env['product.product'].browse(values['description']).name,)
                if values.get('note'):
                    msg += "<li>" + _("Description") + ": %s -> %s <br/>" % (line.note, values['note'],)
                if values.get('actual_amount'):
                    msg += "<li>" + _("Actual Amt") + ": %s -> %s <br/>" % (line.actual_amount, values['actual_amount'],)
                if values.get('amount'):
                    msg += "<li>" + _("After Discount Amt") + ": %s -> %s <br/>" % (line.amount, values['amount'],)
            msg += "</ul>"
            apps.message_post(body=msg)
        result = super(TreatmentInvoice, self).write(values)
        return result

    @api.multi
    def unlink(self):
        for rec in self:
            msg = "<b> Deleted Payment Lines with Values:</b><ul>"
            if rec.description:
                msg += "<li>" + _("Treatment") + ": %s <br/>" % (rec.description.name,)
            if rec.note:
                msg += "<li>" + _("Description") + ": %s  <br/>" % (rec.note,)
            if rec.actual_amount:
                msg += "<li>" + _("Actual Amt") + ": %s  <br/>" % (rec.actual_amount,)
            if rec.amount:
                msg += "<li>" + _("After Discount Amt") + ": %s  <br/>" % (rec.amount,)
            msg += "</ul>"
            rec.appointment_id.message_post(body=msg)
        return super(TreatmentInvoice, self).unlink()
