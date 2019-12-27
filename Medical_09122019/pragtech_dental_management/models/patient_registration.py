from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class PatientRegistration(models.TransientModel):
    _name = 'patient.registration'

    patient_id = fields.Many2one('medical.patient', 'Patient')
    nationality_id = fields.Many2one('patient.nationality', 'Nationality')
    name_tag = fields.Selection([('Mr.', 'Mr.'),
                                 ('Mrs.', 'Mrs.'),
                                 ('Miss', 'Miss'),
                                 ('Ms.', 'Ms.'),
                                 ('Other', 'Other')], 'Name Tag')
    patient_name = fields.Char("Patient Name", required=True)
    mobile = fields.Char("Mobile 1")
    other_mobile = fields.Char("Mobile 2")
    address = fields.Text("Address")
    qid = fields.Char("QID")
    dob = fields.Date('Date of Birth')
    sex = fields.Selection([('m', 'Male'),
                            ('f', 'Female'), ], 'Gender')
    emergency_name = fields.Char('Name')
    emergency_relation = fields.Char('Relation')
    emergency_phone = fields.Char('Phone')
    language = fields.Selection([('english', 'English'),
                             ('arabic', 'Arabic')], 'Language', required=True, default='english')
    register_signature = fields.Binary(string='Signature', required=True)
    register_date = fields.Date('Date', default=fields.Date.context_today, required=True)
    q1 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Is your health good?')
    q2 = fields.Boolean('Anemia')
    q3 = fields.Boolean('Arthritis, Rheumatism')
    q4 = fields.Boolean('Artificial Joints, Pins')
    q5 = fields.Boolean('Asthma')
    q6 = fields.Boolean('Back pain')
    q7 = fields.Boolean('Cortisone Treatment')
    q8 = fields.Boolean('Cough, Persistent')
    q9 = fields.Boolean('Diabetes')
    q10 = fields.Boolean('Epilepsy')
    q11 = fields.Boolean('Fainting')
    q12 = fields.Boolean('Glaucoma')
    q13 = fields.Boolean('Headaches or Migraine')
    q14 = fields.Boolean('Hemophilia')
    q15 = fields.Boolean('Heart Disease')
    q16 = fields.Boolean('Heart Valve problems')
    q17 = fields.Boolean('Heart Surgery')
    q18 = fields.Boolean('Hepatitis')
    q19 = fields.Boolean('High Blood Pressure')
    q20 = fields.Boolean('HIV')
    q21 = fields.Boolean('Jaw Pain')
    q22 = fields.Boolean('Kidney Disease')
    q23 = fields.Boolean('Pacemaker')
    q24 = fields.Boolean('Prolonged bleeding')
    q25 = fields.Boolean('Respiratory Disease')
    q26 = fields.Boolean('Kidney Problem')
    q27 = fields.Boolean('Liver Problem')
    q28 = fields.Boolean('Thyroid Problem')
    q29 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Serious illness or operations?')
    q30 = fields.Char('When')
    q31 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Other Medical Problems?')
    q32 = fields.Char('Please Specify')
    q33 = fields.Boolean('Latex')
    q34 = fields.Boolean('Local Anesthetic')
    q35 = fields.Boolean('Penicillin')
    q36 = fields.Boolean('Sulfa')
    q37 = fields.Boolean('Aspirin')
    q38 = fields.Boolean('Brufen')
    q39 = fields.Boolean('Iodine')
    q40 = fields.Boolean('NONE')
    q41 = fields.Char('Any other allergies')
    q42 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Do you smoke?')
    q43 = fields.Integer(' # of cigarette/day')
    q44 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Are you pregnant?')
    q45 = fields.Char('Month')
    q46 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Are you having discomfort at this time?')
    q47 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Have you ever had any serious trouble?')
    q48 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Are you taking any anticoagulants (blood thinner) ? ')
    q49 = fields.Date('Date of Last Medical Visit?')
    q50 = fields.Char('Brushing')
    q51 = fields.Char('Flossing')
    q52 = fields.Char('Mouthwash')
    q53 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Have you been treated for gum disease?')
    q54 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Have you had any Medical radiographs?')
    q55 = fields.Char('When and where')
    q56 = fields.Char('What is the main reason for seeking Medical care?')
    q57 = fields.Boolean('Bleeding or sore gums')
    q58 = fields.Boolean('Biting Cheeks/lips')
    q59 = fields.Boolean('Broken filling')
    q60 = fields.Boolean('Clenching/grinding')
    q61 = fields.Boolean('Clicking/Locked Jaw')
    q62 = fields.Boolean('Difficult to open/close')
    q63 = fields.Boolean('Frequent blisters (lips/mouth)')
    q64 = fields.Boolean('Food impaction')
    q65 = fields.Boolean('Food collection in between teeth')
    q66 = fields.Boolean('Root Canal Treatment')
    q67 = fields.Boolean('Loose teeth')
    q68 = fields.Boolean('Swelling or Lumps in mouth')
    q69 = fields.Boolean('Ortho Treatment (braces)')
    q70 = fields.Boolean('Sensitive to hot')
    q71 = fields.Boolean('Sensitive to cold')
    q72 = fields.Boolean('Sensitive to sweet')
    q73 = fields.Boolean('Sensitive to bite')
    q74 = fields.Boolean('Shifting in bite')
    q75 = fields.Boolean('Unpleasant taste/bad breath')
    q76 = fields.Selection([('YES', 'YES'), ('NO', 'NO')],
                           'Are you pleased with the general appearance of your teeth and smile?')
    q77 = fields.Char('if no why')

    @api.onchange('patient_id')
    def onchange_patient(self):
        if self.patient_id:
            if self.patient_id.name_tag:
                self.name_tag = self.patient_id.name_tag
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
            if self.patient_id.language:
                self.language = self.patient_id.language
            if self.patient_id.sex:
                self.sex = self.patient_id.sex
            if self.patient_id.emergency_name:
                self.emergency_name = self.patient_id.emergency_name
            if self.patient_id.emergency_relation:
                self.emergency_relation = self.patient_id.emergency_relation
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
            self.emergency_relation = False
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


class ReportSign(models.AbstractModel):
    _name = 'report.pragtech_dental_management.report_registration_pdf'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['medical.patient'].browse(data['ids'])
        return {
            'doc_ids': self.ids,
            'doc_model': 'patient.by.procedure.wizard',
            'data': data,
            'docs': docs,
        }