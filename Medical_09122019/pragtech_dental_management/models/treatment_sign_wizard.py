from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class SignWizard(models.TransientModel):
    _name = 'treatment.sign.wizard'

    digital_signature = fields.Binary(string='Signature', required=True)
    treatment = fields.Char("Treatment", readonly=True)
    doctor = fields.Char("Doctor", readonly=True)
    patient = fields.Char("Patient", readonly=True)
    updated_date = fields.Date('Updated Date', default=fields.Date.context_today, required=True)

    @api.multi
    def action_confirm(self):
        act_id = self.env.context.get('active_ids', [])
        treatment = self.env['medical.teeth.treatment'].search([('id', 'in', act_id)])
        if not self.digital_signature or self.digital_signature == "iVBORw0KGgoAAAANSUhEUgAAAiYAAACWCAYAAADqm0MaA" \
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
        treatment.write({'signature': self.digital_signature,
                         'updated_date':self.updated_date,
                         'wizard_treatment': self.treatment,
                         'wizard_doctor': self.doctor,
                       })
        treatment.print_consent()
