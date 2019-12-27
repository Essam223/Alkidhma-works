from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class SignWizard(models.TransientModel):
    _name = 'sign.wizard'

    language = fields.Selection([('english', 'English'),
                                 ('arabic', 'Arabic')], 'Language', required=True, default='english')
    patient_id = fields.Many2one('medical.patient', 'Patient', required=True)
    digital_signature = fields.Binary(string='Signature', required=True)
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
    q76 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Are you pleased with the general appearance of your teeth and smile?')
    q77 = fields.Char('if no why')
    updated_date = fields.Date('Updated Date', default=fields.Date.context_today, required=True)

    @api.multi
    def action_confirm(self):
        vals = self.read()[0]
        patient = self.patient_id
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
        del vals['patient_id']
        patient.write(vals)
        patient.print_questionnaire()


class ReportSign(models.AbstractModel):
    _name = 'report.pragtech_dental_management.report_signature_pdf'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['medical.patient'].browse(data['ids'])
        return {
            'doc_ids': self.ids,
            'doc_model': 'patient.by.procedure.wizard',
            'data': data,
            'docs': docs,
        }