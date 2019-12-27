from odoo import api, fields, models


class CardReportWizard(models.TransientModel):
    _name = "card.report"

    period_start = fields.Date("Period From", required=True, default=fields.Date.context_today)
    period_stop = fields.Date("Period To", required=True, default=fields.Date.context_today)

    def _get_company_id(self):
        domain_company = []
        company_ids = None
        group_multi_company = self.env.user.has_group('base.group_multi_company')
        if group_multi_company:
            company_ids = [x.id for x in self.env['res.company'].search([('id', 'in', self.env.user.company_ids.ids)])]
            domain_company = [('id', 'in', company_ids)]
        else:
            domain_company = [('id', '=', self.env.user.company_id.id)]
        return domain_company

    company_id = fields.Many2one('res.company', "Company", domain=_get_company_id, required=True)

    @api.model
    def default_get(self, fields):
        res = super(CardReportWizard, self).default_get(fields)
        self._get_company_id()
        res['company_id'] = self.env.user.company_id.id
        return res
    @api.multi
    def card_report(self):
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'company_id': [self.company_id.id, self.company_id.name],
                }
        return self.env.ref('card_charges_management.card_report').report_action(self, data=data)


class ReportAdvPayment(models.AbstractModel):
    _name = 'report.card_charges_management.card_report_pdf'

    @api.model
    def get_adv_payment_details(self, period_start=False, period_stop=False, company_id=False):
        dom = [
            ('payment_date', '>=', period_start),
            ('payment_date', '<=', period_stop),
            ('state', '=', 'posted'),
            ('company_id', '=', company_id[0]),
        ]
        payment_records = self.env['card.charges'].search(dom)
        return {
            'orders': payment_records,
            'period_start':  period_start,
            'period_stop':  period_stop,
            'company_id': company_id,
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_adv_payment_details(data['period_start'],
                                                 data['period_stop'],
                                                 data['company_id'],
                                                 ))
        return data
