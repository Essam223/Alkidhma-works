# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MedicalDoseUnit(models.Model):
    _name = "medical.dose.unit"

    name = fields.Char('Unit', size=32, required=True, )
    desc = fields.Char('Description', size=64)

    _sql_constraints = [
        ('dose_name_uniq', 'unique(name)', 'The Unit must be unique !'),
    ]


class MedicalDrugForm(models.Model):
    _name = "medical.drug.form"

    name = fields.Char('Form', size=64, required=True, )
    code = fields.Char('Code', size=32)

    _sql_constraints = [
        ('drug_name_uniq', 'unique(name)', 'The Name must be unique !'),
    ]


class MedicalMedicationDosage(models.Model):
    _name = "medical.medication.dosage"
    _description = "Medicament Common Dosage combinations"

    name = fields.Char('Frequency', size=256, help='Common frequency name', required=True, )
    code = fields.Char('Code', size=64, help='Dosage Code, such as SNOMED, 229798009 = 3 times per day')
    abbreviation = fields.Char('Abbreviation', size=64,
                               help='Dosage abbreviation, such as tid in the US or tds in the UK')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The Unit already exists')]
