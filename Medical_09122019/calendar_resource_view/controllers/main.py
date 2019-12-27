# -*- coding: utf-8 -*-

import json
import logging
_logger = logging.getLogger(__name__)

import odoo.http as http
from odoo.http import request


class FetchTimeSchedule(http.Controller):

    @http.route('/current_schedule', type='http', auth="public", website=True)
    def fetch_time_schedule(self, **kwargs):
        ICPSudo = request.env['ir.config_parameter']
        start = ICPSudo.get_param(
            'calendar_resource_view.calendar_start'
        )
        end = ICPSudo.get_param(
            'calendar_resource_view.calendar_end'
        )
        start = start and start or "9:00"
        end = end and end or "17:00"
        return start + "," + end

    @http.route('/rooms/list', type='http', auth="public")
    def fetch_rooms(self, **kwargs):
        cr = request.env.cr
        cr.execute("SELECT name, id "
                   "FROM medical_hospital_oprating_room ")
        res = cr.dictfetchall()
        users = request.env['res.users'].search([])
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'name': user.name
            })
        cr.execute("SELECT rp.name, mp.id, mp.qid, rp.mobile, mp.patient_id "
                   "FROM medical_patient mp "
                   "JOIN res_partner rp  ON(mp.name=rp.id) "
                   "WHERE mp.name IS NOT NULL ")
        patients = cr.dictfetchall()
        result = [res, user_list, request.env.user.id, patients]
        return result and json.dumps(result) or '[[], [], 1, []]'

    @http.route('/rooms/list/update', type='http', auth="public")
    def update_rooms(self, **kwargs):
        if not kwargs.get('ids'):
            return
        data = json.loads(kwargs['ids'])
        pat_ids = []
        user_ids = []
        room_ids = []
        try:
            pat_ids = data[0]
            user_ids = data[1]
            room_ids = data[1]
        except:
            pass
        cr = request.env.cr
        cr.execute("SELECT name, id "
                   "FROM medical_hospital_oprating_room "
                   "WHERE id NOT IN %s",
                   (tuple(room_ids), ))
        res = cr.dictfetchall()
        users = request.env['res.users'].search([
            ('id', 'not in', user_ids)
        ])
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'name': user.name
            })
        cr.execute("SELECT rp.name, mp.id, mp.qid, rp.mobile, mp.patient_id "
                   "FROM medical_patient mp "
                   "JOIN res_partner rp  ON(mp.name=rp.id) "
                   "WHERE mp.id NOT IN %s AND "
                   " mp.name IS NOT NULL ",
                   (tuple(pat_ids), ))
        patients = cr.dictfetchall()
        result = [res, user_list, patients]
        return result and json.dumps(result) or '[[], [], []]'
