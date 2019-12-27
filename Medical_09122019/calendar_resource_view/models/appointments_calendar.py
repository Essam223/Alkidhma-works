# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import models, fields, api, exceptions, _


class ConfigCalendar(models.TransientModel):
    _inherit = 'res.config.settings'

    calendar_start = fields.Char(string="Day starting time", default="09:00")
    calendar_end = fields.Char(string="Day ending time", default="17:00")
    # timing = fields.Char(string="Time schedule", readonly=True)

    @api.model
    def get_values(self):
        res = super(ConfigCalendar, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        calendar_start = ICPSudo.get_param(
            'calendar_resource_view.calendar_start'
        )

        calendar_end = ICPSudo.get_param(
            'calendar_resource_view.calendar_end'
        )
        # timing = (calendar_start and calendar_start
        #           or "00:00") + " to " + (calendar_end and
        #                                   calendar_end or "24:00")

        res.update(
            calendar_start=calendar_start,
            calendar_end=calendar_end
        )
        return res

    @api.multi
    def set_values(self):
        min_start = None
        min_end = None
        try:
            min_start = self.calendar_start.split(":")[1]
            min_end = self.calendar_start.split(":")[1]
        except:
            raise exceptions.UserError(_('Invalid time input'))

        if (int(min_start) % 15) != 0:
            raise exceptions.UserError(_('Start time minute should be multiple of 15'))
        if (int(min_end) % 15) != 0:
            raise exceptions.UserError(_('End time minute should be multiple of 15'))
        super(ConfigCalendar, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("calendar_resource_view.calendar_start", self.calendar_start)
        ICPSudo.set_param("calendar_resource_view.calendar_end", self.calendar_end)
        # self.timing = (self.calendar_start and self.calendar_start
        #                or "00:00") + " to " + (self.calendar_end and
        #                                        self.calendar_end or "24:00")
        # ICPSudo.set_param("calendar_resource_view.timing", self.timing)


class AppontmentsCalendar(models.Model):
    _name = 'appointments.calendar'

    name = fields.Char(string="Name", default="Status Colors")

    @api.model
    def get_formview_id(self):
        """fetching the form view id, which will
         be opened when we click the events in the calendar
         :return : view id"""
        try:
            view_id = self.env.ref('pragtech_dental_management.medical_appointment_view').id
        except Exception as e:
           view_id = super(AppontmentsCalendar, self).get_formview_id()
        return view_id

    def find_states(self):
        """fetching states, with their color"""
        StateObj = self.env['appointment.state.color']
        labels = {}
        for state in StateObj._fields['state'].selection:
            labels[state[0]] = state[1]
        result = []
        vals = []
        # for rec in StateObj.search([('state', '!=', None)], order='state asc'):
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
        if self.env.user.has_group('pragtech_dental_management.group_dental_mng_menu'):
            is_group = True
        return is_group

    @api.model
    def action_your_appointments(self):
        """triggering the calendar action"""
        states = self.find_states()
        cr = self._cr
        doc_ids = None
        other_hcare_grps = self.find_hcare_groups()
        if self.env.user.has_group('pragtech_dental_management.group_dental_doc_menu') and not other_hcare_grps:
            partner_ids = [self.env.user.partner_id.id]
            if partner_ids:
                doc_ids = [x.id for x in self.env['medical.physician'].search([('name', 'in', partner_ids)])]
            if doc_ids:
                cr.execute("select D.id:: VARCHAR as id, P.name as name, T.id as dept "
                       "from medical_physician D, res_partner P, medical_department T "
                       # "where D.name= P.id and D.department_id = T.id;")
                        " where D.name= P.id and D.active is true and D.department_id = T.id and D.id in %s "
                       "ORDER BY P.name ASC;", (tuple(doc_ids),))
        else:
            cr.execute("select D.id:: VARCHAR as id, P.name as name, T.id as dept "
                       "from medical_physician D, res_partner P, medical_department T "
                       "where D.name= P.id and D.active is true and D.department_id = T.id ORDER BY P.name ASC;")
        resources = cr.dictfetchall()
        resource_ids = [i['id'] for i in resources]
        cr.execute("select D.id:: VARCHAR as id, P.name as name from medical_patient D, res_partner P "
                   "where D.name= P.id and D.id is not null and D.name is not null")
        patients = cr.dictfetchall()
        state_names = []
        for state in states[1]:
            if state != 'missed' and state != 'cancel':
                state_names.append(state)
        cr.execute('select id:: VARCHAR as id, name as name from medical_department ORDER BY name ASC')
        departments = cr.dictfetchall()
        return {
            'type': 'ir.actions.client',
            'tag': 'calendar_appointments',
            'status': states and states[0] or [],
            'state_names': state_names,
            'resources': resources,
            'resource_ids': resource_ids,
            'patients': patients,
            'departments': departments
        }

    @api.model
    def update_time_range(self, start, end):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("calendar_resource_view.calendar_start", start)
        ICPSudo.set_param("calendar_resource_view.calendar_end", end)
        # timing = (end and end
        #           or "00:00") + " to " + (end and
        #                                   end or "24:00")
        # ICPSudo.set_param("calendar_resource_view.timing", timing)
        result = self.find_time_range()
        return result

    def find_time_range(self):
        """Finds time range configured in the backend
        """
        ICPSudo = self.env['ir.config_parameter'].sudo()
        start = ICPSudo.get_param(
            'calendar_resource_view.calendar_start'
        )
        end = ICPSudo.get_param(
            'calendar_resource_view.calendar_end'
        )
        start = start and start.split(" ")
        end = end and end.split(" ")
        start_hour = start[0] if start else 9
        start_min = start[2] if start else 0

        end_hour = end[0] if end else 17
        end_min = end[2] if end else 0
        return [str(start_hour) + ":" + str(start_min) + ":00", str(end_hour) + ":" + str(end_min) + ":00"]

    @api.model
    def fetch_resources(self):
        """Fetching doctors list"""
        cr = self._cr
        cr.execute("select id:: VARCHAR , name from medical_physician where active is true")
        result = cr.dictfetchall()

        return result

    def fetch_appointments(self, day, month, year, mode, states, resource_ids):
        """Fetching appointments list from db"""
        cr = self._cr

        result = []
        # ================NEEDS FIX ===================
        # NEED TO CREATE A FIELD WHICH STORES THE COLOR CODE ASSOCIATED WITH EACH INVOICE
        # AND INCLUDE IT IN THE QUERY
        try:
            select_query = "select ma.id:: VARCHAR as id," \
                           " ma.patient_name as title, " \
                           " ma.comments as notes, " \
                           " ma.patient_phone as mobile, " \
                           " ma.doctor:: VARCHAR as resource," \
                           " (EXTRACT (DAY FROM ma.appointment_sdate AT TIME ZONE 'UTC')," \
                           " EXTRACT (MONTH FROM ma.appointment_sdate AT TIME ZONE 'UTC') - 1, " \
                           " EXTRACT (YEAR FROM ma.appointment_sdate AT TIME ZONE 'UTC')," \
                           " EXTRACT (HOUR FROM ma.appointment_sdate AT TIME ZONE 'UTC'), " \
                           " EXTRACT (MINUTE FROM ma.appointment_sdate AT TIME ZONE 'UTC')) as start, " \
                           " (EXTRACT (DAY FROM ma.appointment_edate AT TIME ZONE 'UTC'), " \
                           " EXTRACT (MONTH FROM ma.appointment_edate AT TIME ZONE 'UTC') - 1, " \
                           " EXTRACT (YEAR FROM ma.appointment_edate AT TIME ZONE 'UTC'), " \
                           " EXTRACT (HOUR FROM ma.appointment_edate AT TIME ZONE 'UTC'), " \
                           " EXTRACT (MINUTE FROM ma.appointment_edate AT TIME ZONE 'UTC')) as end, " \
                           " ma.color  " \
                           " from medical_appointment ma where active is true "
            if mode == 'resourceAgendaDay' or mode == 'day':
                select_query += " and ma.appointment_sdate is not null and " \
                                " date(ma.appointment_sdate AT TIME ZONE 'UTC') >= %s "
                query_vals = [str(year)+"-"+str(month)+"-"+str(day)]
                if states:
                    select_query += " and ma.state in %s "
                    query_vals.append(tuple(states))
                if resource_ids:
                    select_query += " and ma.doctor in %s "
                    query_vals.append(tuple(resource_ids))
                cr.execute(select_query, tuple(query_vals))

            elif mode == 'month' or mode == 'week':
                select_query += " and ma.appointment_sdate is not null and " \
                                "extract(month from date(ma.appointment_sdate AT TIME ZONE 'UTC')) = %s "
                query_vals = [month]
                if states:
                    select_query += " and ma.state in %s "
                    query_vals.append(tuple(states))
                if resource_ids:
                    select_query += " and ma.doctor in %s "
                    query_vals.append(tuple(resource_ids))
                cr.execute(select_query, tuple(query_vals))

            result = cr.dictfetchall()
        except:
            return []
        for rec in result:
            rec['model'] = 'medical.appointment'
            reg_patient = self.env['medical.appointment'].browse(int(rec['id'])).patient
            if reg_patient:
                rec['file_no'] = reg_patient.patient_id
            if not reg_patient:
                rec['file_no'] = ""
            rec['start'] = (rec['start'][1:-1]).split(",")
            rec['end'] = (rec['end'][1:-1]).split(",")
        return result

    @api.model
    def find_appointments(self,
                          day, month,
                          year, mode,
                          states,
                          resource_ids):
        """
        we are fetching the appointments and time schedule
         from the db according to the details provided
        :param day: we need to fetch this day's details
        :param month: the month
        :param year: year of the appointments
        :param mode: view mode of the calendar
        :param states: filter appointments by state
        :param resource_ids: filter appointments by doctor
        :return:
        list containing appointments and time schedule
        """
        events = self.fetch_appointments(day, month, year, mode, states, resource_ids)
        timeslots = self.find_time_range()
        # not removing the next few lines just for understanding the common parameters that can be passed
        # in the events list
        # events = [{
        #     'id': 11,
        #     'title': 'Long Event',
        #     'start': [year, month, day, 11, 0],
        #     'end': [year, month, day, 11, 15],
        #     'resource': 'doctor2',
        #     'color': '#ea2ec2'
        return [events, timeslots]

    @api.model
    def update_appointment_end(self, event_id, days, hours, minutes):
        AppointmentsObj = self.env['medical.appointment']
        rec = AppointmentsObj.browse(event_id)
        if rec.appointment_edate:
            rec.appointment_edate = datetime.strptime(
                rec.appointment_edate,
                "%Y-%m-%d %H:%M:%S") + timedelta(days=days)
            rec.appointment_edate = datetime.strptime(
                rec.appointment_edate,
                "%Y-%m-%d %H:%M:%S") + timedelta(hours=hours)
            rec.appointment_edate = datetime.strptime(
                rec.appointment_edate,
                "%Y-%m-%d %H:%M:%S") + timedelta(minutes=minutes)
        return False
    @api.model
    def update_appointment(self, event_id, days, hours, minutes):
        AppointmentsObj = self.env['medical.appointment']
        rec = AppointmentsObj.browse(event_id)
        if rec.appointment_sdate:
            rec.appointment_sdate = datetime.strptime(
                rec.appointment_sdate,
                "%Y-%m-%d %H:%M:%S") + timedelta(days=days)
            rec.appointment_sdate = datetime.strptime(
                rec.appointment_sdate,
                "%Y-%m-%d %H:%M:%S") + timedelta(hours=hours)
            rec.appointment_sdate = datetime.strptime(
                rec.appointment_sdate,
                "%Y-%m-%d %H:%M:%S") + timedelta(minutes=minutes)
        if rec.appointment_edate:
            rec.appointment_edate = datetime.strptime(
                rec.appointment_edate,
                "%Y-%m-%d %H:%M:%S") + timedelta(days=days)
            rec.appointment_edate = datetime.strptime(
                rec.appointment_edate,
                "%Y-%m-%d %H:%M:%S") + timedelta(hours=hours)
            rec.appointment_edate = datetime.strptime(
                rec.appointment_edate,
                "%Y-%m-%d %H:%M:%S") + timedelta(minutes=minutes)
        return False


class AppointmentColorConfig(models.Model):
    _name = 'appointment.state.color'

    state = fields.Selection([
        ('draft', 'Booked'), ('confirmed', 'Confirmed'), ('missed', 'Missed'),
        ('checkin', 'Checked In'), ('ready', 'In Chair'), ('done', 'Completed'),
        ('visit_closed', 'Visit Closed'), ('cancel', 'Canceled')
    ], string="Status")
    color = fields.Char(string="Color")


class AppointmentExtended(models.Model):
    _inherit = 'medical.appointment'

    color = fields.Char(default='rgba(115,138,230,0.59)',
                        compute='_get_color',
                        store=True)

    @api.depends('state')
    @api.multi
    def _get_color(self):
        for appt in self:
            if appt.state:
                state_obj = self.env['appointment.state.color'].search([('state', '=', appt.state)], limit=1)
                if state_obj:
                    appt.update({
                        'color': state_obj.color
                    })
