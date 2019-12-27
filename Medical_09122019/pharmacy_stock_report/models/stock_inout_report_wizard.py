from odoo import api, fields, models
from datetime import datetime


class StockReportWizard(models.TransientModel):
    _name = "pharmacy.stock_inout.report"

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

    @api.multi
    def pharmacy_stock_inout_report(self):
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'company_id': self.company_id.id,
            'company_name': self.company_id.name,
        }
        return self.env.ref('pharmacy_stock_report.pharmacy_stock_inout_report').report_action(self, data=data)


class ReportStock(models.AbstractModel):
    _name = 'report.pharmacy_stock_report.pharmacy_stock_inout_report_pdf'

    @api.model
    def get_stock_details(self, period_start=False, period_stop=False, company_id=False):

        products = self.env['product.product'].search([('is_medicament', '=', True)])
        product_moves = self.env['stock.move'].search([('product_id', 'in', products.ids),
                                                       ('company_id', '=', company_id),
                                                       ('date', '>=', period_start),
                                                       ('date', '<=', period_stop),
                                                       ('state', '<=', 'done'),
                                                       ])
        product_moves_dict = {}
        open_stock = []
        for products in product_moves:
            open_stock.append(self.env['product.product'].with_context(to_date=period_start).search(
                [('id', '=', products.product_id.id)]))

        for moves in product_moves:
            qty_in = 0
            qty_out = 0
            if moves.location_id.usage == "internal":
                qty_out = moves.quantity_done
            elif moves.location_dest_id.usage == "internal":
                qty_in = moves.quantity_done

            qty_in_previous = 0
            qty_out_previous = 0
            if moves.product_id.name in product_moves_dict.keys():
                if product_moves_dict[moves.product_id.name]['qty_in']:
                    qty_in_previous = product_moves_dict[moves.product_id.name]['qty_in']

                if product_moves_dict[moves.product_id.name]['qty_out']:
                    qty_out_previous = product_moves_dict[moves.product_id.name]['qty_out']

            product_moves_dict[moves.product_id.name] = {'qty_available': moves.product_id.qty_available,
                                                         'qty_in': qty_in_previous + qty_in,
                                                         'qty_out': qty_out_previous + qty_out,
                                                         'open_qty': 0
                                                         }

        for lines in open_stock:
            for product in product_moves_dict:
                if product == lines.name:
                    product_moves_dict[lines.name]['open_qty'] = lines.qty_available

        return {'orders': product_moves_dict}

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_stock_details(data['period_start'],
                                           data['period_stop'], data['company_id']))
        data['period_start'] = datetime.strptime(data['period_start'], '%Y-%m-%d')
        data['period_stop'] = datetime.strptime(data['period_stop'], '%Y-%m-%d')
        return data
