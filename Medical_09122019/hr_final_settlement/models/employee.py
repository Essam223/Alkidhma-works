from odoo import api, models, fields,_
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def action_terminate(self):
        if not self.wage:
            raise UserError(_('Please define Basic salary for this employee.'))
        if not self.joining_date:
            raise UserError(_('Please define Joining date for this employee.'))
        contextt = {}
        contextt['default_employee_id'] = self.id
        contextt['default_joining_date'] = self.joining_date
        return {
            'name': _('Termination details'),
            'view_id': self.env.ref('hr_final_settlement.view_termination_wizard_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'termination.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }