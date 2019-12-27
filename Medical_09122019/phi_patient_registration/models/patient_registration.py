from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class PatientRegistration(models.TransientModel):
    _inherit = 'patient.registration'

    language = fields.Selection([('english', 'English'),
                                 ('arabic', 'Arabic')], 'Language', required=True, default='english')
    patient_name = fields.Char("Name", required=True)
    qid = fields.Char("QID No.")
    patient_id = fields.Many2one('medical.patient', 'Patient')
    sex = fields.Selection([('m', 'Male'),
                            ('f', 'Female'), ], 'Gender')
    mobile = fields.Char("Mobile 1")
    nationality_id = fields.Many2one('patient.nationality', 'Nationality')
    marital_status = fields.Selection(
        [('s', 'Single'), ('m', 'Married'), ('w', 'Widowed'), ('d', 'Divorced'), ('x', 'Separated'), ],
        'Marital Status')
    address = fields.Text("Address")
    occupation_id = fields.Many2one('medical.occupation', 'Occupation')
    dob = fields.Date('Date of Birth')
    other_mobile = fields.Char("Mobile 2")
    emergency_name = fields.Char('Person to contact in case of emergency')
    emergency_phone = fields.Char('Mob')
    register_signature = fields.Binary(string='Signature', required=True)
    register_date = fields.Date('Date', default=fields.Date.context_today, required=True)
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
    p23 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Have you ever had any unusual reaction to anesthetic or drug (like penisilin)')
    p24 = fields.Text('Is there any other information you wish to add?')
    register_signature = fields.Binary(string='Signature', required=False)

    @api.onchange('patient_id')
    def onchange_patient(self):
        if self.patient_id:
            if self.patient_id.patient_name:
                self.patient_name = self.patient_id.patient_name
            if self.patient_id.mobile:
                self.mobile = self.patient_id.mobile
            if self.patient_id.other_mobile:
                self.other_mobile = self.patient_id.other_mobile
            if self.patient_id.address:
                self.address = self.patient_id.address
            if self.patient_id.qid:
                self.qid = self.patient_id.qid
            if self.patient_id.dob:
                self.dob = self.patient_id.dob
            if self.patient_id.sex:
                self.sex = self.patient_id.sex
            if self.patient_id.emergency_name:
                self.emergency_name = self.patient_id.emergency_name
            if self.patient_id.emergency_phone:
                self.emergency_phone = self.patient_id.emergency_phone
        else:
            self.patient_name = False
            self.mobile = False
            self.other_mobile = False
            self.address = False
            self.qid = False
            self.dob = False
            self.sex = False
            self.emergency_name = False
            self.emergency_phone = False

    @api.multi
    def action_confirm(self):
        vals = self.read()[0]
        patient_obj = self.env['medical.patient']
        # if not self.register_signature or self.register_signature == "iVBORw0KGgoAAAANSUhEUgAAAiYAAACWCAYAAADqm0MaA" \
        #                                                                "AAHZ0lEQVR4Xu3YMYpUYRSE0dcbEhnQ/ccjiMyGNJdJJv" \
        #                                                                "vqcjruoP5TNyje6/EjQIAAAQIECEQEXpEcYhAgQIAAAQI" \
        #                                                                "EHsPEERAgQIAAAQIZAcMkU4UgBAgQIECAgGHiBggQIECA" \
        #                                                                "AIGMgGGSqUIQAgQIECBAwDBxAwQIECBAgEBGwDDJVCEIA" \
        #                                                                "QIECBAgYJi4AQIECBAgQCAjYJhkqhCEAAECBAgQMEzcAA" \
        #                                                                "ECBAgQIJARMEwyVQhCgAABAgQIGCZugAABAgQIEMgIGCa" \
        #                                                                "ZKgQhQIAAAQIEDBM3QIAAAQIECGQEDJNMFYIQIECAAAEC" \
        #                                                                "hokbIECAAAECBDIChkmmCkEIECBAgAABw8QNECBAgAABA" \
        #                                                                "hkBwyRThSAECBAgQICAYeIGCBAgQIAAgYyAYZKpQhACBA" \
        #                                                                "gQIEDAMHEDBAgQIECAQEbAMMlUIQgBAgQIECBgmLgBAgQ" \
        #                                                                "IECBAICNgmGSqEIQAAQIECBAwTNwAAQIECBAgkBEwTDJV" \
        #                                                                "CEKAAAECBAgYJm6AAAECBAgQyAgYJpkqBCFAgAABAgQME" \
        #                                                                "zdAgAABAgQIZAQMk0wVghAgQIAAAQKGiRsgQIAAAQIEMg" \
        #                                                                "KGSaYKQQgQIECAAAHDxA0QIECAAAECGQHDJFOFIAQIECB" \
        #                                                                "AgIBh4gYIECBAgACBjIBhkqlCEAIECBAgQMAwcQMECBAg" \
        #                                                                "QIBARsAwyVQhCAECBAgQIGCYuAECBAgQIEAgI2CYZKoQh" \
        #                                                                "AABAgQIEDBM3AABAgQIECCQETBMMlUIQoAAAQIECBgmbo" \
        #                                                                "AAAQIECBDICBgmmSoEIUCAAAECBAwTN0CAAAECBAhkBAy" \
        #                                                                "TTBWCECBAgAABAoaJGyBAgAABAgQyAoZJpgpBCBAgQIAA" \
        #                                                                "AcPEDRAgQIAAAQIZAcMkU4UgBAgQIECAgGHiBggQIECAA" \
        #                                                                "IGMgGGSqUIQAgQIECBAwDBxAwQIECBAgEBGwDDJVCEIAQ" \
        #                                                                "IECBAgYJi4AQIECBAgQCAjYJhkqhCEAAECBAgQMEzcAAE" \
        #                                                                "CBAgQIJARMEwyVQhCgAABAgQIGCZugAABAgQIEMgIGCaZ" \
        #                                                                "KgQhQIAAAQIEDBM3QIAAAQIECGQEDJNMFYIQIECAAAECh" \
        #                                                                "okbIECAAAECBDIChkmmCkEIECBAgAABw8QNECBAgAABAh" \
        #                                                                "kBwyRThSAECBAgQICAYeIGCBAgQIAAgYyAYZKpQhACBAg" \
        #                                                                "QIEDAMHEDBAgQIECAQEbAMMlUIQgBAgQIECBgmLgBAgQI" \
        #                                                                "ECBAICNgmGSqEIQAAQIECBAwTNwAAQIECBAgkBEwTDJVC" \
        #                                                                "EKAAAECBAgYJm6AAAECBAgQyAgYJpkqBCFAgAABAgQMEz" \
        #                                                                "dAgAABAgQIZAQMk0wVghAgQIAAAQKGiRsgQIAAAQIEMgK" \
        #                                                                "GSaYKQQgQIECAAAHDxA0QIECAAAECGQHDJFOFIAQIECBA" \
        #                                                                "gIBh4gYIECBAgACBjIBhkqlCEAIECBAgQMAwcQMECBAgQ" \
        #                                                                "IBARsAwyVQhCAECBAgQIGCYuAECBAgQIEAgI2CYZKoQhA" \
        #                                                                "ABAgQIEDBM3AABAgQIECCQETBMMlUIQoAAAQIECBgmboA" \
        #                                                                "AAQIECBDICBgmmSoEIUCAAAECBAwTN0CAAAECBAhkBAyT" \
        #                                                                "TBWCECBAgAABAoaJGyBAgAABAgQyAoZJpgpBCBAgQIAAA" \
        #                                                                "cPEDRAgQIAAAQIZAcMkU4UgBAgQIECAgGHiBggQIECAAI" \
        #                                                                "GMgGGSqUIQAgQIECBAwDBxAwQIECBAgEBGwDDJVCEIAQI" \
        #                                                                "ECBAgYJi4AQIECBAgQCAjYJhkqhCEAAECBAgQMEzcAAEC" \
        #                                                                "BAgQIJARMEwyVQhCgAABAgQIGCZugAABAgQIEMgIGCaZK" \
        #                                                                "gQhQIAAAQIEDBM3QIAAAQIECGQEDJNMFYIQIECAAAECho" \
        #                                                                "kbIECAAAECBDIChkmmCkEIECBAgAABw8QNECBAgAABAhk" \
        #                                                                "BwyRThSAECBAgQICAYeIGCBAgQIAAgYyAYZKpQhACBAgQ" \
        #                                                                "IEDAMHEDBAgQIECAQEZgbph8/Pn9/vd5fmQEBSFAgAABA" \
        #                                                                "lGB1/P8+vb97Wc03qexDJOltmQlQIAAAQJfEDBMvoDlrw" \
        #                                                                "QIECBAgACB/wXmvpiokAABAgQIELgrYJjc7dbLCBAgQID" \
        #                                                                "AnIBhMleZwAQIECBA4K6AYXK3Wy8jQIAAAQJzAobJXGUC" \
        #                                                                "EyBAgACBuwKGyd1uvYwAAQIECMwJGCZzlQlMgAABAgTuC" \
        #                                                                "hgmd7v1MgIECBAgMCdgmMxVJjABAgQIELgrYJjc7dbLCB" \
        #                                                                "AgQIDAnIBhMleZwAQIECBA4K6AYXK3Wy8jQIAAAQJzAob" \
        #                                                                "JXGUCEyBAgACBuwKGyd1uvYwAAQIECMwJGCZzlQlMgAAB" \
        #                                                                "AgTuChgmd7v1MgIECBAgMCdgmMxVJjABAgQIELgrYJjc7" \
        #                                                                "dbLCBAgQIDAnIBhMleZwAQIECBA4K6AYXK3Wy8jQIAAAQ" \
        #                                                                "JzAobJXGUCEyBAgACBuwKGyd1uvYwAAQIECMwJGCZzlQl" \
        #                                                                "MgAABAgTuChgmd7v1MgIECBAgMCdgmMxVJjABAgQIELgr" \
        #                                                                "YJjc7dbLCBAgQIDAnIBhMleZwAQIECBA4K6AYXK3Wy8jQ" \
        #                                                                "IAAAQJzAv8A4B4MlzhRUicAAAAASUVORK5CYII=":
        #     raise UserError(_('Please enter your signature and confirm !!!'))
        if self.register_signature != "iVBORw0KGgoAAAANSUhEUgAAAiYAAACWCAYAAADqm0MaA" \
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
            vals['register_signature'] = self.register_signature
        if self.nationality_id:
            vals['nationality_id'] = self.nationality_id.id
        if self.occupation_id:
            vals['occupation_id'] = self.occupation_id.id
        if self.register_date:
            del vals['register_date']
            vals['updated_date'] = self.register_date
        if not self.patient_id:
            vals['patient_id'] = 'New'
            if self.register_date:
                vals['register_date'] = self.register_date
            patient_id = patient_obj.create(vals)
            patient_id.attach_registration()
        else:
            del vals['patient_id']
            self.patient_id.write(vals)
            self.patient_id.attach_registration()
