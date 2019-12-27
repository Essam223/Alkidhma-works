from odoo import api, fields, models, tools, _


class PatientRegistration(models.Model):
    _inherit = 'medical.patient'

    p1 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], "Are you under a physician's care now?")
    p2 = fields.Text('Give a reason for treatment')
    p3 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], "Are you taking any kind of medication?")

    p4 = fields.Boolean('Asthma')
    p5 = fields.Boolean('Anemia')
    p6 = fields.Boolean('Hypertension')
    p7 = fields.Boolean('Diabetes')
    p8 = fields.Boolean('Infectious dis.')
    p9 = fields.Boolean('Allergy')
    p10 = fields.Boolean('Epilepsy')
    p11 = fields.Boolean('Eye Dis.')
    p12 = fields.Boolean('Tuberculosis')
    p13 = fields.Boolean('Kidney Dis.')
    p14 = fields.Boolean('Heart Dis.')
    p15 = fields.Boolean('Liver Dis.')
    p16 = fields.Text('Other diseases you would like to mention')
    p17 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Are you pregnant?')
    p18 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Have you ever had surgery before?')
    p19 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Have you ever had blood transfusion?')
    p20 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Have you ever had trouble with prolonged bleeding?')
    p21 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Have you ever had fainting during surgical procedure?')
    p22 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Local anesthesia or injection?')
    p23 = fields.Selection([('YES', 'YES'), ('NO', 'NO')],
                           'Have you ever had any unusual reaction to anesthetic or drug (like penisilin)')
    p24 = fields.Text('Is there any other information you wish to add?')
