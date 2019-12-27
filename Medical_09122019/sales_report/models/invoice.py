from odoo import api, models, SUPERUSER_ID
from datetime import date
import base64


class MedicalInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def _send_sales_report(self, cron_mode=True):
        date_today = date.today()
        data = {
            'date_type': 'invoice',
            'period_start': date_today,
            'period_stop': date_today,
            'doctor': False,
            'patient': False,
            'insurance_company': False,
            'payment_mode': False,
            'cashier': False,
            'company_id': [self.env.user.company_id.id, self.env.user.company_id.name],
        }
        REPORT_ID = 'sales_report.sales_report'
        pdf = self.env.ref(REPORT_ID).render_qweb_pdf(self.ids, data=data)
        b64_pdf = base64.b64encode(pdf[0])
        ATTACHMENT_NAME = 'Daily Sales Report'
        attachment_id = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'datas_fname': ATTACHMENT_NAME + '.pdf',
            'store_fname': ATTACHMENT_NAME,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        attach = {
            attachment_id.id,
        }
        user = self.env['res.users'].browse(SUPERUSER_ID)
        from_email = user.partner_id.email
        mail_values = {
            'reply_to': from_email,
            'email_to': from_email,
            'subject': ATTACHMENT_NAME,
            'body_html': """<div>
            <p>Hello,</p>
            <p>This email was created automatically by Odoo H Care. Please find the attached sales reports.</p>
            </div>
            <div>Thank You</div>""",
            'attachment_ids': [(6, 0, attach)]
        }
        mail_id = self.env['mail.mail'].create(mail_values)
        mail_id.send()
