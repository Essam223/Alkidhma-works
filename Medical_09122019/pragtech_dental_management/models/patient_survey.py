from odoo import api, fields, models, _


class PatientSurvey(models.Model):
    _name = 'patient.survey'

    name = fields.Char('Name', required=True)
