# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"
    _description = "Product Category"

    treatment = fields.Boolean('Treatment')

    @api.multi
    def get_treatment_categs(self, insurance, doctor):
        category_domain = [('treatment', '=', True)]
        category_ids = []
        if doctor:
            doc = self.env['medical.physician'].browse(doctor)
            category_ids += doc.treatment_category.ids
        if category_ids:
                category_domain.append(('id', 'in', category_ids))
        all_records = self.search_read(
            category_domain, ['id', 'name'])
        treatment_list = []
        for each_rec in all_records:
            treatment_list.append({
                'treatment_categ_id': each_rec.get('id'),
                'name': each_rec.get('name'),
                'treatments': []
            })

        product_domain = [('is_treatment', '=', True), ('company_id', '=', self.env.user.company_id.id)]
        if insurance:
            ins = self.env['medical.insurance'].browse(insurance)
            treatment_ids = []
            if ins.company_id.treatment_ids:
                treatment_ids += ins.company_id.treatment_ids.ids
            if ins.company_id.non_coverage_treatment_ids:
                treatment_ids += ins.company_id.non_coverage_treatment_ids.ids
            if treatment_ids:
                product_domain.append(('id', 'in', treatment_ids))

        # Normal clinic Trearments
        else:
            product_domain.append(('is_clinic_treatment', '=', True))
        product_rec = self.env['product.product'].search_read(
            product_domain, [
                'id', 'name', 'action_perform',
                'categ_id', 'highlight_color'])
        for each_product in product_rec:
            for each_treatment in treatment_list:
                if each_product['categ_id'][0] == each_treatment['treatment_categ_id']:
                    each_treatment['treatments'].append({
                        'treatment_id': each_product.get('id'),
                        'treatment_name': each_product.get('name'),
                        'highlight_color': each_product.get('highlight_color'),
                        'action': each_product.get('action_perform')
                    })
                    break
        final_list = []
        for lst in treatment_list:
            if lst.get('treatments'):
                final_list.append(lst)
        return final_list
