from odoo import api, fields, models
from datetime import datetime, timedelta
from dateutil import relativedelta
import time


class StockReportWizard(models.TransientModel):
    _name = "stock.report"

    period_start = fields.Datetime("Period From", required=True, default=time.strftime('%Y-%m-01'))
    period_stop = fields.Datetime("Period To", required=True,
                              default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    product_ids = fields.Many2many('product.product', string='Products')
    location_ids = fields.Many2many('stock.location', string='Locations', domain=[('usage', '=', 'internal')])
    type_in_out = fields.Selection([('In', 'In'), ('Out', 'Out'), ('In_and_Out', 'In and Out')], string='Type',
                                   default='In_and_Out', required=True)

    @api.multi
    def stock_consumption_report(self):
        dom_loc_id_list = []
        dom_loc_name_list = []
        for locat in self.location_ids:
            dom_loc_id_list.append(locat.id)
            dom_loc_name_list.append(locat.display_name)
        dom_prod_id_list = []
        dom_prod_name_list = []
        for prod in self.product_ids:
            dom_prod_id_list.append(prod.id)
            dom_prod_name_list.append(prod.name)
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'location_ids': dom_loc_id_list,
            'location_names': dom_loc_name_list,
            'product_ids': dom_prod_id_list,
            'product_names': dom_prod_name_list,
            'type_in_out': self.type_in_out,

                }
        return self.env.ref('stock_consumption_report.report_stock_consumption_pdf').report_action(self, data=data)


class ReportStockReport(models.AbstractModel):

    _name = 'report.stock_consumption_report.report_stock_consumption'

    def get_qty_done_in_total(self, stock_m_line_in):
        qty_done_in = 0.0
        for m_line_in in stock_m_line_in:
            qty_done_in += m_line_in.qty_done
        return qty_done_in

    def get_qty_done_out_total(self, stock_m_line_out):
        qty_done_out = 0.0
        for m_line_out in stock_m_line_out:
            qty_done_out += m_line_out.qty_done
        return qty_done_out

    @api.model
    def get_stock_details(self, period_start=False, period_stop=False, location_ids=False, location_names=False,
                           product_ids=False, product_names=False, type_in_out=False):
        dom_in = [('date', '>=', period_start),('date', '<=', period_stop),('state', '=', 'done'),
               ('location_dest_id.usage', '=', 'internal')]
        dom_out = [('date', '>=', period_start), ('date', '<=', period_stop), ('state', '=', 'done'),
                   ('location_id.usage', '=', 'internal')]
        dom_loc = [('usage', '=', 'internal')]
        if location_ids:
            dom_loc.append(('id', 'in', location_ids))
            dom_in.append(('location_dest_id.id', 'in', location_ids))
            dom_out.append(('location_id.id', 'in', location_ids))
        if product_ids:
            dom_in.append(('product_id', 'in', product_ids))
            dom_out.append(('product_id', 'in', product_ids))
        locations = self.env['stock.location'].search(dom_loc)
        location_in_list = []
        move_line_in = {}
        for i in locations:
            location_in_list.append(i)
            move_line_in[i] = {'IN': [], 'OUT': []}
        stock_m_line_in = self.env['stock.move.line'].search(dom_in, order="date asc")
        for m_l_in in stock_m_line_in:
            move_line_in[m_l_in.location_dest_id]['IN'].append(m_l_in)
        stock_m_line_out = self.env['stock.move.line'].search(dom_out, order="date asc")
        for m_l_out in stock_m_line_out:
            move_line_in[m_l_out.location_id]['OUT'].append(m_l_out)

        period_start = datetime.strptime(period_start, '%Y-%m-%d %H:%M:%S')
        period_stop = datetime.strptime(period_stop, '%Y-%m-%d %H:%M:%S')
        locat_name = ""
        for loc_name in location_names:
            if locat_name != '':
                locat_name += ', '
            locat_name += loc_name
        product_name = ""
        for prod_name in product_names:
            if product_name != '':
                product_name += ', '
            product_name += prod_name
        return {
            'period_start': period_start,
            'type_in_out': type_in_out,
            'period_stop': period_stop,
            'location_names': locat_name,
            'product_names': product_name,
            'get_qty_done_out_total': self.get_qty_done_out_total,
            'locations' : location_in_list,
            'stock_m_line_in': move_line_in,
            'get_qty_done_in_total': self.get_qty_done_in_total,
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_stock_details(data['period_start'],
                                          data['period_stop'], data['location_ids'], data['location_names']
                                           , data['product_ids'], data['product_names'], data['type_in_out']))
        return data
