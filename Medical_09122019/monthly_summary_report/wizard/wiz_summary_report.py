from odoo import api, fields, models
from datetime import datetime
import calendar


class MonthlySummaryWizard(models.TransientModel):
    _name = "monthly.summary.wizard"

    @api.model
    def default_get(self, fields):
        res = super(MonthlySummaryWizard, self).default_get(fields)
        current_month = datetime.today().month
        current_year = datetime.now().year
        last_day_of_month = calendar.monthrange(current_year,  current_month)[1]
        first_day = datetime(current_year, current_month, 1)
        last_day = datetime(current_year, current_month, last_day_of_month)
        res['period_start'] = first_day
        res['period_stop'] = last_day
        return res

    period_start = fields.Date("Period From", required=True)
    period_stop = fields.Date("Period To", required=True)

    @api.multi
    def print_report(self):
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            }
        return self.env.ref('monthly_summary_report.summary_report').report_action(self, data=data)