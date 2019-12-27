# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models


class ViewExtended(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('scheduler', "Scheduler")])


class ActWindowViewExtended(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('scheduler', "Scheduler")])


class CalenderSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    schedule_start = fields.Char(string="Schedule start", default='06:00')
    schedule_end = fields.Char(string="Schedule end", default='17:00')
    manage_breaktime = fields.Boolean(string="Manage break", default=False)
    break_start = fields.Char(string="Break start", default='12:00')
    break_end = fields.Char(string="Break end", default='14:00')


class CalendarConfig(models.Model):
    _name = 'calender.config'

    @api.model
    def update_calendar_schedule(self, time_slot):
        """Updates the calendar time schedule"""
        self.env['ir.config_parameter'].sudo().set_param(
            'calendar_scheduler.schedule_start', str(time_slot[0]))
        self.env['ir.config_parameter'].sudo().set_param(
            'calendar_scheduler.schedule_end', str(time_slot[1]))

        # Updates the calendar break time schedule
        self.env['ir.config_parameter'].sudo().set_param(
            'calendar_scheduler.manage_breaktime', str(time_slot[2]))
        self.env['ir.config_parameter'].sudo().set_param(
            'calendar_scheduler.break_start', str(time_slot[3]))
        self.env['ir.config_parameter'].sudo().set_param(
            'calendar_scheduler.break_end', str(time_slot[4]))
        return True

    @api.model
    def find_doctor_ids(self):
        resource_ids = []
        cr = self._cr
        other_hcare_grps = self.find_hcare_groups()
        if other_hcare_grps:
            cr.execute("select D.id "
                       " from medical_physician D,"
                       " res_partner P, medical_department T "
                       "where D.name= P.id and D.active is true and"
                       " T.company_id=%s and "
                       "D.department_id = T.id ORDER BY P.name ASC",
                       (self.env.user.company_id.id,))
            resources = cr.dictfetchall()
            resource_ids = [i['id'] for i in resources]
        else:
            doctor_by_user = (
                self.env.user.physician_ids.ids if self.env.user.physician_ids
                else [])
            if doctor_by_user:
                cr.execute("select D.id "
                           " from medical_physician D,"
                           " res_partner P, medical_department T "
                           "where D.id in %s and "
                           "D.name= P.id and D.active is true and"
                           " D.company_id=%s and "
                           "D.department_id = T.id ORDER BY P.name ASC",
                           (tuple(doctor_by_user),
                            self.env.user.company_id.id))
                resources = cr.dictfetchall()
                resource_ids = [i['id'] for i in resources]
        return resource_ids

    @api.model
    def search_read_data(self):
        """Gathers the data required for calendar initialisation
        :returns {
            resources: columns used to group the calendar dayview,
            time_schedule: calendar time schedule,
            services: services involved,
            customers: customers list
        }
        """
        cr = self._cr
        states = self.find_states()
        state_names = []
        for state in states[1]:
            # if state != 'missed' and state != 'cancel':
            state_names.append(state)

        doc_ids = None
        other_hcare_grps = self.find_hcare_groups()
        # #####################################################
        #  old code commented out
        # #####################################################
        # if (self.env.user.has_group(
        #         'pragtech_dental_management.group_dental_doc_menu') and
        #         not other_hcare_grps):
        #     partner_ids = [self.env.user.partner_id.id]
        #     if partner_ids:
        #         doc_ids = [x.id for x in self.env[
        #           'medical.physician'].search(
        #             [('name', 'in', partner_ids)])]
        #     if doc_ids:
        #         cr.execute("select D.id:: VARCHAR as id, P.name as name, "
        #                    "P.id as p_id, P.name as title, "
        #                    "T.id as dept, T.name as dname "
        #                    "from medical_physician D,"
        #                    " res_partner P, medical_department T "
        #                    # "where D.name= P.id and
        #                    D.department_id = T.id;")
        #                    " where D.name= P.id and D.active is true and "
        #                    "D.department_id = T.id and D.id in %s "
        #                    "ORDER BY P.name ASC;", (tuple(doc_ids),))
        resources = []
        resource_ids = []
        if other_hcare_grps:
            cr.execute("select D.id:: VARCHAR as id, P.name as name, "
                       "P.id as p_id, P.name as title, "
                       "T.id as dept, T.name as dname "
                       "from medical_physician D,"
                       " res_partner P, medical_department T "
                       "where D.name= P.id and D.active is true and D.company_id=%s and "
                       "D.department_id = T.id ORDER BY P.name ASC", (self.env.user.company_id.id,))
            resources = cr.dictfetchall()
            resource_ids = [i['id'] for i in resources]
        else:
            doctor_by_user = (
                self.env.user.physician_ids.ids if self.env.user.physician_ids
                else [])
            if doctor_by_user:
                cr.execute("select D.id:: VARCHAR as id, P.name as name, "
                           "P.id as p_id, P.name as title, "
                           "T.id as dept, T.name as dname "
                           "from medical_physician D,"
                           " res_partner P, medical_department T "
                           "where D.id in %s and "
                           "D.name= P.id and D.active is true and D.company_id=%s and "
                           "D.department_id = T.id ORDER BY P.name ASC",
                           (tuple(doctor_by_user),self.env.user.company_id.id ))
                resources = cr.dictfetchall()
                resource_ids = [i['id'] for i in resources]
        rooms = []
        room_ids = []
        if other_hcare_grps:
            cr.execute("select name, id, name as title "
                       "from medical_hospital_oprating_room WHERE company_id=%s "
                       "order by name asc", (self.env.user.company_id.id,))
            rooms = cr.dictfetchall()
            room_ids = [i['id'] for i in rooms]
        else:
            room_by_user = (
                self.env.user.room_ids.ids if self.env.user.room_ids
                else [])
            if room_by_user:
                cr.execute("select name, id, name as title "
                           "from medical_hospital_oprating_room "
                           "where id in %s and company_id=%s "
                           "order by name asc",
                           (tuple(room_by_user),self.env.user.company_id.id ))
                rooms = cr.dictfetchall()
                room_ids = [i['id'] for i in rooms]

        get_param = self.env['ir.config_parameter'].sudo().get_param
        #  fetching time schedule
        time_schedule = {
            'schedule_start': get_param(
                'calendar_scheduler.schedule_start') if get_param(
                'calendar_scheduler.schedule_start') else '6:0',
            'schedule_end': get_param(
                'calendar_scheduler.schedule_end') if get_param(
                'calendar_scheduler.schedule_end') else '17:0'
        }
        #  fetching break schedule
        manage_breaktime = get_param(
            'calendar_scheduler.manage_breaktime') if get_param(
            'calendar_scheduler.manage_breaktime') else False
        break_schedule = {
            'break_start': get_param(
                'calendar_scheduler.break_start') if get_param(
                'calendar_scheduler.break_start') else '12:0',
            'break_end': get_param(
                'calendar_scheduler.break_end') if get_param(
                'calendar_scheduler.break_end') else '14:0'
        }
        # fetching patients
        # cr.execute("SELECT rp.name, mp.id, mp.qid, rp.mobile, mp.patient_id, "
        #            "mp.sex, mp.dob, mp.nationality_id "
        #            "FROM medical_patient mp "
        #            "JOIN res_partner rp  ON(mp.name=rp.id) "
        #            "WHERE mp.name IS NOT NULL ")
        # patients = cr.dictfetchall()
        patients = []
        # departments
        cr.execute('select id:: VARCHAR as id, name as name '
                   'from medical_department WHERE company_id=%s ORDER BY name ASC', (self.env.user.company_id.id,))
        departments = cr.dictfetchall()
        # nationality
        cr.execute("select name, code, id "
                   "from patient_nationality")
        nationality_ids = cr.dictfetchall()
        return [
            resources,
            time_schedule,
            states,
            state_names,
            resource_ids,
            patients,
            departments,
            rooms,
            room_ids,
            resources,
            manage_breaktime,
            break_schedule,
            nationality_ids
        ]

    @api.model
    def add_appointment(self, data):
        """creates an appointment. Called from js"""
        if data:
            order_id = self.env['pos.order'].create(data)
        return order_id.lines.ids

    def find_states(self):
        """fetching states, with their color"""
        StateObj = self.env['appointment.state.color']
        labels = {}
        for state in StateObj._fields['state'].selection:
            labels[state[0]] = state[1]
        result = []
        vals = []
        for rec in StateObj.search([('state', '!=', None)]):
            vals.append(rec.state)
            result.append({
                'state': [rec.state, labels[rec.state]],
                'color': rec.color
            })
        return result and [result, vals] or []

    def find_hcare_groups(self):
        is_group = False
        # Admin/Receptionist
        if (self.env.user.has_group(
                'pragtech_dental_management.group_dental_mng_menu') or
                self.env.user.has_group(
                    'pragtech_dental_management.group_dental_user_menu')):
            is_group = True
        return is_group
