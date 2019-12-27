from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class PlanWizard(models.TransientModel):
    _name = 'treatment.plan.wizard'

    def _get_default_company_id(self):
        return self._context.get('force_company', self.env.user.company_id.id)

    company_id = fields.Many2one('res.company', string='Company',
        default=_get_default_company_id, readonly=True)
    plan_signature = fields.Binary(string='Signature', required=True)
    appt_id = fields.Many2one('medical.appointment', "Appointment", readonly=True)
    doctor = fields.Char("Doctor", readonly=True)
    patient = fields.Char("Patient", readonly=True)
    updated_date = fields.Date('Updated Date', default=fields.Date.context_today, required=True, readonly=True)
    operations = fields.One2many('medical.teeth.treatment', compute='_compute_operations')

    @api.multi
    @api.model
    @api.depends('doctor')
    def _compute_operations(self):
        oper_obj = self.env['medical.teeth.treatment']
        if self.appt_id:
            oper_ids = oper_obj.search([('patient_id', '=', self.appt_id.patient.id), ('state', 'in', ['planned'])])
        else:
            oper_ids = False
        self.operations = oper_ids

    @api.onchange("appt_id")
    def onchange_appt(self):
        for record in self:
            if record.appt_id:
                record.doctor = record.appt_id.doctor.name.name
                record.patient = record.appt_id.patient_name


    @api.multi
    def action_confirm(self):
        act_id = self.env.context.get('active_ids', [])
        appt = self.env['medical.appointment'].search([('id', 'in', act_id)])
        if not self.plan_signature or self.plan_signature == "iVBORw0KGgoAAAANSUhEUgAAAiYAAACWCAYAAADqm0MaA" \
                                                                       "AAHZ0lEQVR4Xu3YMYpUYRSE0dcbEhnQ/ccjiMyGNJdJJv" \
                                                                       "vqcjruoP5TNyje6/EjQIAAAQIECEQEXpEcYhAgQIAAAQI" \
                                                                       "EHsPEERAgQIAAAQIZAcMkU4UgBAgQIECAgGHiBggQIECA" \
                                                                       "AIGMgGGSqUIQAgQIECBAwDBxAwQIECBAgEBGwDDJVCEIA" \
                                                                       "QIECBAgYJi4AQIECBAgQCAjYJhkqhCEAAECBAgQMEzcAA" \
                                                                       "ECBAgQIJARMEwyVQhCgAABAgQIGCZugAABAgQIEMgIGCa" \
                                                                       "ZKgQhQIAAAQIEDBM3QIAAAQIECGQEDJNMFYIQIECAAAEC" \
                                                                       "hokbIECAAAECBDIChkmmCkEIECBAgAABw8QNECBAgAABA" \
                                                                       "hkBwyRThSAECBAgQICAYeIGCBAgQIAAgYyAYZKpQhACBA" \
                                                                       "gQIEDAMHEDBAgQIECAQEbAMMlUIQgBAgQIECBgmLgBAgQ" \
                                                                       "IECBAICNgmGSqEIQAAQIECBAwTNwAAQIECBAgkBEwTDJV" \
                                                                       "CEKAAAECBAgYJm6AAAECBAgQyAgYJpkqBCFAgAABAgQME" \
                                                                       "zdAgAABAgQIZAQMk0wVghAgQIAAAQKGiRsgQIAAAQIEMg" \
                                                                       "KGSaYKQQgQIECAAAHDxA0QIECAAAECGQHDJFOFIAQIECB" \
                                                                       "AgIBh4gYIECBAgACBjIBhkqlCEAIECBAgQMAwcQMECBAg" \
                                                                       "QIBARsAwyVQhCAECBAgQIGCYuAECBAgQIEAgI2CYZKoQh" \
                                                                       "AABAgQIEDBM3AABAgQIECCQETBMMlUIQoAAAQIECBgmbo" \
                                                                       "AAAQIECBDICBgmmSoEIUCAAAECBAwTN0CAAAECBAhkBAy" \
                                                                       "TTBWCECBAgAABAoaJGyBAgAABAgQyAoZJpgpBCBAgQIAA" \
                                                                       "AcPEDRAgQIAAAQIZAcMkU4UgBAgQIECAgGHiBggQIECAA" \
                                                                       "IGMgGGSqUIQAgQIECBAwDBxAwQIECBAgEBGwDDJVCEIAQ" \
                                                                       "IECBAgYJi4AQIECBAgQCAjYJhkqhCEAAECBAgQMEzcAAE" \
                                                                       "CBAgQIJARMEwyVQhCgAABAgQIGCZugAABAgQIEMgIGCaZ" \
                                                                       "KgQhQIAAAQIEDBM3QIAAAQIECGQEDJNMFYIQIECAAAECh" \
                                                                       "okbIECAAAECBDIChkmmCkEIECBAgAABw8QNECBAgAABAh" \
                                                                       "kBwyRThSAECBAgQICAYeIGCBAgQIAAgYyAYZKpQhACBAg" \
                                                                       "QIEDAMHEDBAgQIECAQEbAMMlUIQgBAgQIECBgmLgBAgQI" \
                                                                       "ECBAICNgmGSqEIQAAQIECBAwTNwAAQIECBAgkBEwTDJVC" \
                                                                       "EKAAAECBAgYJm6AAAECBAgQyAgYJpkqBCFAgAABAgQMEz" \
                                                                       "dAgAABAgQIZAQMk0wVghAgQIAAAQKGiRsgQIAAAQIEMgK" \
                                                                       "GSaYKQQgQIECAAAHDxA0QIECAAAECGQHDJFOFIAQIECBA" \
                                                                       "gIBh4gYIECBAgACBjIBhkqlCEAIECBAgQMAwcQMECBAgQ" \
                                                                       "IBARsAwyVQhCAECBAgQIGCYuAECBAgQIEAgI2CYZKoQhA" \
                                                                       "ABAgQIEDBM3AABAgQIECCQETBMMlUIQoAAAQIECBgmboA" \
                                                                       "AAQIECBDICBgmmSoEIUCAAAECBAwTN0CAAAECBAhkBAyT" \
                                                                       "TBWCECBAgAABAoaJGyBAgAABAgQyAoZJpgpBCBAgQIAAA" \
                                                                       "cPEDRAgQIAAAQIZAcMkU4UgBAgQIECAgGHiBggQIECAAI" \
                                                                       "GMgGGSqUIQAgQIECBAwDBxAwQIECBAgEBGwDDJVCEIAQI" \
                                                                       "ECBAgYJi4AQIECBAgQCAjYJhkqhCEAAECBAgQMEzcAAEC" \
                                                                       "BAgQIJARMEwyVQhCgAABAgQIGCZugAABAgQIEMgIGCaZK" \
                                                                       "gQhQIAAAQIEDBM3QIAAAQIECGQEDJNMFYIQIECAAAECho" \
                                                                       "kbIECAAAECBDIChkmmCkEIECBAgAABw8QNECBAgAABAhk" \
                                                                       "BwyRThSAECBAgQICAYeIGCBAgQIAAgYyAYZKpQhACBAgQ" \
                                                                       "IEDAMHEDBAgQIECAQEZgbph8/Pn9/vd5fmQEBSFAgAABA" \
                                                                       "lGB1/P8+vb97Wc03qexDJOltmQlQIAAAQJfEDBMvoDlrw" \
                                                                       "QIECBAgACB/wXmvpiokAABAgQIELgrYJjc7dbLCBAgQID" \
                                                                       "AnIBhMleZwAQIECBA4K6AYXK3Wy8jQIAAAQJzAobJXGUC" \
                                                                       "EyBAgACBuwKGyd1uvYwAAQIECMwJGCZzlQlMgAABAgTuC" \
                                                                       "hgmd7v1MgIECBAgMCdgmMxVJjABAgQIELgrYJjc7dbLCB" \
                                                                       "AgQIDAnIBhMleZwAQIECBA4K6AYXK3Wy8jQIAAAQJzAob" \
                                                                       "JXGUCEyBAgACBuwKGyd1uvYwAAQIECMwJGCZzlQlMgAAB" \
                                                                       "AgTuChgmd7v1MgIECBAgMCdgmMxVJjABAgQIELgrYJjc7" \
                                                                       "dbLCBAgQIDAnIBhMleZwAQIECBA4K6AYXK3Wy8jQIAAAQ" \
                                                                       "JzAobJXGUCEyBAgACBuwKGyd1uvYwAAQIECMwJGCZzlQl" \
                                                                       "MgAABAgTuChgmd7v1MgIECBAgMCdgmMxVJjABAgQIELgr" \
                                                                       "YJjc7dbLCBAgQIDAnIBhMleZwAQIECBA4K6AYXK3Wy8jQ" \
                                                                       "IAAAQJzAv8A4B4MlzhRUicAAAAASUVORK5CYII=":
            raise UserError(_('Please enter your signature and confirm !!!'))
        appt.write({'plan_signature': self.plan_signature,
                    'treatment_plan_date': self.updated_date,
                       })
        appt.attach_treatment_plan()
