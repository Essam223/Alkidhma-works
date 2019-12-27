from odoo import api, fields, models
from datetime import datetime


class StockReportWizard(models.TransientModel):
    _name = "pharmacy.stock.report"

    period_start = fields.Date("Period From", required=True, default=fields.Date.context_today)
    period_stop = fields.Date("Period To", required=True, default=fields.Date.context_today)
    show_no_stock = fields.Boolean(string="Show No Stock Items", )

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

    @api.multi
    def pharmacy_stock_report(self):
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'company_id': self.company_id.id,
            'company_name': self.company_id.name,
            'show_all_product': self.show_no_stock,
        }
        return self.env.ref('pharmacy_stock_report.pharmacy_stock_report').report_action(self, data=data)


class ReportStock(models.AbstractModel):
    _name = 'report.pharmacy_stock_report.pharmacy_stock_report_pdf'

    @api.model
    def get_stock_details(self, period_start=False, period_stop=False, company_id=False, show_all_product=False):

        products = self.env['product.product'].search([('is_medicament', '=', True),
                                                       ('company_id', '=', company_id), ])

        product_lots = self.env['stock.production.lot'].search([('product_id', 'in', products.ids),
                                                                ('life_date', '>=', period_start),
                                                                ('life_date', '<=', period_stop), ])

        product_lots_dict = {}
        for lots in product_lots:
            if lots.product_id.name in product_lots_dict.keys():
                product_lots_dict[lots.product_id.name]['lots'].append(lots)
                product_lots_dict[lots.product_id.name]['total_qty'] += lots.product_qty
            else:
                product_lots_dict[lots.product_id.name] = {'lots': [lots], 'total_qty': lots.product_qty
                                                           }
        if show_all_product:
            for items in products:
                if items.name not in product_lots_dict.keys():
                    product_lots_dict[items.name] = {'lots': [],
                                                     'total_qty': 0}

        return {'product_lots': product_lots_dict}

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_stock_details(data['period_start'],
                                           data['period_stop'],
                                           data['company_id'],
                                           data['show_all_product']))
        data['period_start'] = datetime.strptime(data['period_start'], '%Y-%m-%d')
        data['period_stop'] = datetime.strptime(data['period_stop'], '%Y-%m-%d')
        return data
