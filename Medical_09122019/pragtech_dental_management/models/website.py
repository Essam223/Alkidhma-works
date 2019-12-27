# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import hashlib


class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def get_image(self, a):
        if 'image' in list(a.keys()):
            return True
        else:
            return False

    @api.multi
    def get_type(self, record1):
        categ_type = record1['type']
        categ_ids = self.env['product.category'].search([('name', '=', categ_type)])
        if categ_ids['type'] == 'view':
            return False
        return True

    @api.multi
    def check_next_image(self, main_record, sub_record):
        if len(main_record['image']) > sub_record:
            return 1
        else:
            return 0

    @api.multi
    def image_url_new(self, record1):
        """Returns a local url that points to the image field of a given browse record."""
        lst = []
        size = None
        field = 'datas'
        record = self.env['ir.attachment'].browse(self.ids)
        cnt = 0
        for r in record:
            if r.store_fname:
                cnt = cnt + 1
                model = r._name
                sudo_record = r.sudo()
                id = '%s_%s' % (r.id, hashlib.sha1(
                    (sudo_record.write_date or sudo_record.create_date or '').encode('utf-8')).hexdigest()[0:7])
                if cnt == 1:
                    size = '' if size is None else '/%s' % size
                else:
                    size = '' if size is None else '%s' % size
                lst.append('/website/image/%s/%s/%s%s' % (model, id, field, size))
        return lst
