from odoo import api, models,_
from odoo.exceptions import UserError


class ClaimReport(models.AbstractModel):
    _name='report.basic_insurance.claim_report'
    
    @api.multi
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        inv_records = self.env['account.invoice'].search \
            ([('date_invoice', '>=', from_date),('date_invoice', '<=', to_date),('patient','!=',False)])
        return {
            'doc_ids': self.ids,
            'doc_model': 'dental.claim.wizard',
            'data': data['form'],
            'docs': docs,
            'patients': inv_records,
        }
        
