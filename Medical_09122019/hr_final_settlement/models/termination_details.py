from odoo import api, models, fields


class TerminationDetails(models.Model):
    _name = 'termination.details'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    joining_date = fields.Date('Joining Date')
    last_working_day = fields.Date('Last working day')
    gratuity_days = fields.Float('Gratuity days')
    gratuity_amt = fields.Float('Gratuity amount')
    fully_paid = fields.Boolean('Fully Paid')
    payment_ids = fields.Many2many('account.payment', 'termination_payment_rel', 'termination_id', 'payment_id',
                                   string="Payments", copy=False, readonly=True)
    residual = fields.Float('Due Amount', compute='_compute_residual', copy=False)

    @api.depends('payment_ids')
    def _compute_residual(self):
        for rec in self:
            gratuity_amt = rec.gratuity_amt
            paid_amt = 0
            for line in rec.payment_ids:
                paid_amt += line.amount
            due = gratuity_amt - paid_amt
            rec.residual = due

