function trim (str) {
  return str.replace(/^\s+|\s+$/gm,'');
}

odoo.define('calendar_resource_view.calendar_resource_view', function (require) {
'use strict';

var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var Widget = require('web.Widget');
var rpc = require('web.rpc');

var operators = {
    '+': function(a, b) { return a + b },
    '-': function(a, b) { return a - b }
};

var AppointmentsToday = Widget.extend(ControlPanelMixin, {
    title: core._t("Today's Appointments"),
    template: 'appointments_today',

    events: {
        'click .fc-prev-button': 'on_prev_day',
        'click .fc-next-button': 'on_next_day',
        'click .fc-resourceAgendaDay-button': 'on_resource_day',
        'click .fc-month-button': 'on_click_month',
        'click .fc-agendaWeek-button': 'on_click_week',
        'click .fc-agendaDay-button': 'on_click_agenda_day',
        'click .sub-prev': 'on_click_prev_sub',
        'click .sub-next': 'on_click_next_sub',
        'click .update_date_range': 'update_time_range',
        'click button.hide_ctrl_panel': 'hide_panel',
        'click button.button-reload': 'reload_calendar',
        'mouseover button.button-reload': 'toggle_refresh_button',
        'mouseout button.button-reload': 'toggle_refresh_button',
        'change .state_selection': 'filter_events',
        'change .dept_selection': 'filter_dept',
        'change .dept_select_all': 'select_all_dept',
        'change .resource_selection': 'filter_resources',
        'change .res_select_all': 'select_all_res',
        'change .patient_type': 'change_patient_type',
        'change .followup_app': 'onchange_followup_app',
        'change .appt_start': 'get_followup_app_start',
        'change .modalPhysician': 'get_followup_modalPhysician',
        // 'click .res_unselect_all': 'unselect_all_res',
        'click .event_popup': 'popup_close',
        'click .close': 'modal_close',
        'click .close2': 'modal_close',
        'keydown .patient_phone': 'keydown_phone',
        'keydown .patient_name': 'keydown_name',
        'keydown .qid': 'keydown_qid',
        'keydown .patient_ids': 'keydown_patient_ids'
        // 'click .o_form_button_save': 'test'
    },
    autocomplete_method: function (el, key) {
        var self = this;
        function split(val) {
            return val.split(/,\s*/);
        }
        function extractLast(term) {
            return split(term).pop();
        }
        var reg_patient = $('.patient_type').prop('checked');
        $(el).autocomplete({
            select: function (event, ui) {
                var terms = split(this.value);
                // remove the current input
                terms.pop();
                // add the selected item
                terms.push(ui.item.label);
                this.value = terms;
                self.onchange_patient(ui.item.value);
                var patient =  ui.item.value;
                var appointment_sdate =  $('.app_start input').val();
                var doctor =  $('.modalPhysician').val();
                self.followup_function(patient, appointment_sdate, doctor, 'New')
                return false;
            },
            source: function (request, response) {
                // delegate back to autocomplete, but extract the last term
                if (reg_patient === true) {
                    var res = $.ui.autocomplete.filter(
                        self[key], extractLast(request.term));
                    response(res);
                }
                else {
                    response([]);
                }
            }
        });
    },
    keydown_phone: function () {
        this.autocomplete_method(
            '.patient_phone',
            'phone_no'
        );
    },
    keydown_name: function () {
        this.autocomplete_method(
            '.patient_name',
            'pat_names'
        );
    },
    keydown_qid: function () {
        this.autocomplete_method(
            '.qid',
            'qid'
        );
    },
    keydown_patient_ids: function () {
        this.autocomplete_method(
            '.patient_ids',
            'pat_ids'
        );
    },
    onchange_patient: function(p_id){
        var patient = this.patients[p_id];
        $('.patient_list').val(patient.id);
        $('.patient_name').val(patient.name);
        $('.qid').val(patient.qid);
        $('.patient_phone').val(patient.mobile);
        $('.patient_ids').val(patient.patient_id);
    },
    toggle_refresh_button: function (evt) {
        if($('button.button-reload i').hasClass('fa-spin') == true){
            $('button.button-reload i').removeClass("fa-spin");
        }
        else{
            $('button.button-reload i').addClass("fa-spin");
        }
    },
    hide_panel: function (evt) {
        if($('.hide_ctrl_panel').hasClass('hide_panel') == true){
            $('#appointments_container_sub').css('display', 'block');
            $('.calendar_properties').css('display', 'block');
            $('#appointments_container').css('width', '81%');
            $('.hide_ctrl_panel').removeClass("hide_panel");
            $('.hide_ctrl_panel').css('margin-top', '4.2%');

            $('button.hide_ctrl_panel i.fa-chevron-circle-left').addClass('fa-close');
            $('button.hide_ctrl_panel i.fa-chevron-circle-left').removeClass('fa-chevron-circle-left');
        }
        else{
            $('#appointments_container_sub').css('display', 'none');
            $('.calendar_properties').css('display', 'none');
            $('#appointments_container').css('width', '99%');
            $('.hide_ctrl_panel').addClass("hide_panel");
            $('.hide_ctrl_panel').css('margin-top', '1%');

            $('button.hide_ctrl_panel i.fa-close').addClass('fa-chevron-circle-left');
            $('button.hide_ctrl_panel i.fa-close').removeClass('fa-close');
        }

    },
    modal_close: function(){
        var self = this;
        var d = self.current_time.getDate();
        var m = self.current_time.getMonth();
        var y = self.current_time.getFullYear();
        $('#appointments_container').fullCalendar2('destroy');
        $('#calendarModal').modal('hide');
        self.get_options(d, parseInt(m)+1, y, self.state_names, self.resource_ids);
        $('.app_start input').val('');
        $('.app_end input').val('');
        $('.patient_name').val('');
        $('.patient_list').val('');
        $('.urgent_app').prop('checked',false);
        $('.followup_app').prop('checked',false);
        $('.rooms_list').find('option').remove();
        $('.modal_created_by').find('option').remove();
        $('.required_field_warning').css({
            'display': 'none'
        });
        $('.patient_name').css('border-color', 'lightgray');
    },
    popup_close: function(event){
        var self = this, patient = false;

        if ($('input.patient_type').prop("checked") == true) {
            patient = parseInt($('.patient_list').val());
        }
        var vals = {
            patient : patient,
            is_registered : $('input.patient_type').prop("checked"),
            appointment_sdate: $('.app_start input').val(),
            appointment_edate: $('.app_end input').val(),
            patient_name: $('.patient_name').val(),
            patient_state: $('.patient_stat').val(),
            patient_phone: $('.patient_phone').val(),
            qid: $('.qid').val(),
            doctor: $('.modalPhysician').val(),
            room_id: $('.rooms_list').val(),
            urgency: $('.urgent_app').prop("checked"),
            salesperson_id: $('.modal_created_by').val(),
            followup: $('.followup_app').prop("checked"),
            comments: $('.Notes').val(),
        };

        var missing_values = false;
        if(vals['is_registered'] === false) {
            if (!vals['patient_name']) {
                missing_values = true;
                $('.patient_name').css('border-color', 'red');
            }
        }
        else{
        if (vals['patient']){
        console.log("have patient");
        }else{
        missing_values = true;
        $('.patient_name').css('border-color', 'red');
        }
        }
        if (!vals['doctor']) {
            missing_values = true;
            $('.modalPhysician').css('border-color', 'red');
        }
        if (!vals['appointment_sdate']) {
            missing_values = true;
            $('.app_start input').css('border-color', 'red');
        }
        if (!vals['patient_state']) {
            missing_values = true;
            $('.patient_stat').css('border-color', 'red');
        }

        if (missing_values === true) {
            $('.required_field_warning').css({
                'display': 'block'
            });
        }
        else{
            var temp;
//            if (vals['appointment_sdate']  >=  vals['appointment_edate']){
//                alert('Appointment Start Date must be before Appointment End Date !')
//                return false;
//            }
            temp = new Date(vals['appointment_sdate']);
            vals['appointment_sdate'] = temp.toUTCString();
            if (vals['appointment_edate']) {
                temp = new Date(vals['appointment_edate']);
                vals['appointment_edate'] = temp.toUTCString();
            }

            rpc.query({
                model: 'medical.appointment',
                method: 'create',
                args: [vals]
            }).then(function (res) {
                if(res){
                    var d = self.current_time.getDate();
                    var m = self.current_time.getMonth();
                    var y = self.current_time.getFullYear();
                    $('#appointments_container').fullCalendar2('destroy');
                    self.get_options(d, parseInt(m)+1, y, self.state_names, self.resource_ids);
                    $('#calendarModal').modal('hide');
                    $('.app_start input').val('');
                    $('.app_end input').val('');
                    $('.patient_name').val('');
                    $('.patient_list').val('');
                    $('.urgent_app').prop('checked',false);
                    $('.followup_app').prop('checked',false);
                    $('.patient').find('option').remove();
                    $('.rooms_list').find('option').remove();
                    $('.modal_created_by').find('option').remove();
                    $('.required_field_warning').css({
                        'display': 'none'
                    });
                }
            });
        }
    },
    reload_calendar: function () {
        var self = this;
        this.rerender_events();

        $.ajax({
            url: "/rooms/list/update",
            data: {ids: "[["+Object.keys(self.patients) + "],[" +self.user_ids + "],[" + self.room_ids+"]]" },
            success: function(result) {
                self.rooms = JSON.parse(result)[0];
                var $el = $(".rooms_list");
                $.each(self.rooms, function(r) {
                    self.room_ids.push(self.rooms[r]['id']);
                    $el.append($("<option></option>")
                            .attr("value", self.rooms[r]['id']).text(self.rooms[r]['name']));
                });

                self.users = JSON.parse(result)[1];
                $el = $(".modal_created_by");
                $.each(self.users, function(u) {
                    self.user_ids.push(self.users[u]['id']);
                    $el.append($("<option></option>")
                                        .attr("value", self.users[u]['id']).text(self.users[u]['name']));
                });

                var patients = JSON.parse(result)[2];
                // var $patient_el = $(".patient_list");
                $.each(patients, function(p) {
                    /*$patient_el.append($("<option></option>")
                            .attr("value", patients[p]['id']).text(patients[p]['name']));*/
                    // self.patient_ids.push(self.patients[p]['id']);
                    self.patients[patients[p]['id']] = patients[p];
                    if(patients[p]['mobile']){
                        self.phone_no.push({label:patients[p]['mobile'], value:patients[p]['id']});
                    }
                    if(patients[p]['qid']){
                        self.qid.push({label:patients[p]['qid'], value:patients[p]['id']});
                    }
                    self.pat_names.push({label:patients[p]['name'], value:patients[p]['id']});
                    self.pat_names.push({label:patients[p]['name'], value:patients[p]['id']});
                });
            }});
    },
    select_all_dept: function (event) {
        var checked = event.currentTarget ? event.currentTarget.checked : true;
        if(checked == true){
            this._select_all_dept(event);
            $(".res_select_all").prop('checked', true);
        }
        else if (checked == false){
            this._unselect_all_dept(event);
            $(".res_select_all").prop('checked', false);
        }
        this.select_all_res(event)
    },
    _select_all_dept: function (ev) {
        $('.dept_selection').each(function() {
            $(this).prop('checked', true);
            $('.resource_selection').each(function() {
                if ($(this).parent().hasClass('invisible')) {
                    $(this).parent().removeClass("invisible").addClass("visible");
                    $(this).parent().show();
                    $(this).prop('checked', true);
                }
                /*$(this).trigger('change');*/
            });
        });
    },
    _unselect_all_dept: function (ev) {
        $(".dept_selection").prop('checked', false);
        $('.resource_selection').each(function() {
            if ($(this).parent().hasClass('visible')) {
                $(this).parent().removeClass("visible").addClass("invisible");
                $(this).parent().hide();
                $(this).prop('checked', false);
            }
            /*$(this).trigger('change');*/
        });
    },
    select_all_res: function (event) {
        var checked = event.currentTarget ? event.currentTarget.checked : true;
        if(checked == true){
            this._select_all_res(event);
        }
        else if (checked == false){
            this._unselect_all_res(event);
        }

    },
    _select_all_res: function (ev) {
        if (this.excluded_res_ids){
            $(".resource_selection").prop('checked', true);
            for(var i in this.excluded_res_ids){
                this.resource_ids.push(i);
                this.resources.push(this.excluded_res_ids[i]);
            }
        }
        this.excluded_res_ids = [];
        $('#appointments_container').fullCalendar2('destroy');
        this.get_options(
            this.current_time.getDate(),
            parseInt(this.current_time.getMonth())+1,
            this.current_time.getFullYear(),
            this.state_names,
            this.resource_ids
        );
    },
    _unselect_all_res: function (ev) {
        if (this.resource_ids){
            $(".resource_selection").prop('checked', false);
            for(var r=0;r<this.resources.length; r++){
                var res = this.resources[r];
                this.excluded_res_ids[res['id']] = res;
            }
        }
        this.resources = [];
        this.resource_ids = [];
        $('#appointments_container').fullCalendar2('destroy');
        this.get_options(
            this.current_time.getDate(),
            parseInt(this.current_time.getMonth())+1,
            this.current_time.getFullYear(),
            this.state_names,
            this.resource_ids
        );
    },
    filter_events: function (event) {
        var checked = event.currentTarget ? event.currentTarget.checked : true;
        var checked_id = event.currentTarget ? event.currentTarget.id : '';
        if(checked == false){
            this.state_names.splice( this.state_names.indexOf(checked_id), 1 );
        }
        if(checked == true){
            this.state_names.push(checked_id);
        }
        $('#appointments_container').fullCalendar2('destroy');
        this.get_options(
            this.current_time.getDate(),
            parseInt(this.current_time.getMonth())+1,
            this.current_time.getFullYear(),
            this.state_names,
            this.resource_ids
        );
    },
    followup_function: function(patient, appointment_sdate, doctor, name){
       var temp;
       temp = new Date(appointment_sdate);
       if ( appointment_sdate[2]== '/'){
           var month_app = appointment_sdate.split("/")[0]
       }
       else{
           var month_app = appointment_sdate.split("-")[1]
       }
       var date_app = temp.toUTCString().split(" ")[1]
       var year_app = temp.toUTCString().split(" ")[3]
       var time_app = temp.toUTCString().split(" ")[4]
       var new_date = year_app.concat("-")
       new_date = new_date.concat(month_app)
       new_date = new_date.concat("-")
       new_date = new_date.concat(date_app)
       new_date = new_date.concat(" ")
       new_date = new_date.concat(time_app)
        rpc.query({
            model: 'medical.appointment',
            method: 'funct_followup',
            args: [patient, patient, new_date, doctor, name],
        })
        .then(function(follow_up_expired) {
            var is_follow_up = follow_up_expired[0]
            var is_expired_up = follow_up_expired[1]
            if (is_follow_up == 1){
                $(".followup_app").prop("checked", true);
                var message = 'This can be a followup visit';
            }
            else{
                $('.followup_app').prop('checked',false);
                if (is_expired_up == 1){
                    var message = 'Followup expired';
                }
                else{
                    var message =  'This is not a followup visit';
                }
            }
            alert(message);
        });
    },
    onchange_followup_app: function () {
        if($(".followup_app").prop("checked")== true){
            $('.followup_app').prop('checked',false);
            alert("You cant make this Appointment Followup");
        }

    },
    get_followup_app_start: function () {
            console.log("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee..........", $('.app_start input').val())
            var patient =  $('.patient_list').val();
            var appointment_sdate =  $('.app_start input').val();
            var doctor =  $('.modalPhysician').val();
            this.followup_function(patient, appointment_sdate, doctor, 'New')
    },
    get_followup_modalPhysician: function () {
            var patient =  $('.patient_list').val();
            var appointment_sdate =  $('.app_start input').val();
            var doctor =  $('.modalPhysician').val();
            this.followup_function(patient, appointment_sdate, doctor, 'New')
    },
    change_patient_type: function () {
        var checked = $('input.patient_type').prop("checked");
        if (checked == true) {
            $('.box.patient').css('visibility', 'visible');
            $('.patient_ids').val('');
            $('.patient_name').val('');
            $('.patient_list').val('');
            $('.patient_phone').val('');
            $('.qid').val('');
        }
        else{
            $('.patient_ids').val('');
            $('.patient_name').val('');
            $('.patient_list').val('');
            $('.patient_phone').val('');
            $('.qid').val('');
            $('.box.patient').css('visibility', 'hidden');
        }
    },
    filter_dept: function (event) {
        $('.dept_selection').each(function() {
            if ($(this).is(":checked")) {
                $(".dept_select_all").prop('checked', false);
            }
        });
        if (event.currentTarget) { 
            var dept_id = event.currentTarget.id
            $('.resource_selection').each(function() {
                if ($(this).parent().hasClass(dept_id)) {
                    $(this).prop('checked', false);
                    if ($(this).parent().hasClass("visible")) {
                        $(this).parent().removeClass("visible").addClass("invisible");
                        $(this).parent().hide();
                    }
                    else {
                        $(this).parent().removeClass("invisible").addClass("visible");
                        $(this).parent().show();
                        $(this).prop('checked', true);
                    }
                    $(this).trigger('change');
                }
            });
        }
    },
    filter_resources: function (event) {
        var checked = event.currentTarget ? event.currentTarget.checked : true;
        var checked_resource = event.currentTarget ? event.currentTarget.id : '';
        $('.resource_selection').each(function() {
            if ($(this).is(":checked")) {
                $(".res_select_all").prop('checked', false);
            }
        });

        if(checked == false){
            this.resource_ids.splice( this.resource_ids.indexOf(checked_resource), 1 );
            for(var r=0;r<this.resources.length; r++){
                var res = this.resources[r];
                if(res['id'] == checked_resource){
                    this.excluded_res_ids[checked_resource] = res;
                    this.resources.splice( this.resources.indexOf(res), 1 );
                }
            }
        }
        if(checked == true){
            var temp = this.excluded_res_ids[checked_resource];
            this.resources.push(temp);
            this.resource_ids.push(checked_resource);
            delete this.excluded_res_ids[checked_resource];
        }
        $('#appointments_container').fullCalendar2('destroy');
        this.get_options(
            this.current_time.getDate(),
            parseInt(this.current_time.getMonth())+1,
            this.current_time.getFullYear(),
            this.state_names,
            this.resource_ids
        );
    },
    go_to_current_day: function () {
        this.current_time = new Date();
        $('#appointments_container').fullCalendar2( 'today');
        this.rerender_events();
    },
    update_time_range: function(){
        var minute;
        var date_input = $('#date_start').val().trim();
        minute = date_input.split(":")[1];
        if((parseInt(minute) % 15) != 0){
            alert("Minute should be multiple of 15");
            return;
        }
        date_input = $('#date_end').val().trim();
        minute = date_input.split(":")[1];
        if((parseInt(minute) % 15) != 0){
            alert("Minute should be multiple of 15");
            return;
        }
        var self = this;
        var new_start = $('#date_start').val().trim();
        var new_end = $('#date_end').val().trim();
        rpc.query({
            model: 'appointments.calendar',
            method: 'update_time_range',
            args: [new_start, new_end]
        }).done(function(result){
            var d = self.current_time.getDate();
            var m = self.current_time.getMonth();
            var y = self.current_time.getFullYear();
            $('#appointments_container').fullCalendar2('destroy');
            self.get_options(d, parseInt(m)+1, y, this.state_names, this.resource_ids);
        });
    },

    init: function(parent, action) {
        this.status = action.status || [];
        this.state_names = action.state_names || [];
        this.resources = action.resources || [];
        this.patients = action.patients || [];
        this.resource_ids = action.resource_ids || [];
        this.departments = action.departments || [];
        this.excluded_res_ids = {};
        this.current_time = new Date();
        this.view_mode = 'resourceAgendaDay';
        // this.helper_cal = false;
        this.patients = {};
        // this.patient_ids = [];
        this.phone_no = [];
        this.qid = [];
        this.pat_names = [];
        this.rooms = [];
        this.room_ids = [];
        this.users = [];
        this.user_ids = [];
        this.pat_ids = [];
        // this.events_list = [];
        this.uid = null;
        var self = this;
        $.ajax({url: "/rooms/list", success: function(result) {
            self.rooms = JSON.parse(result)[0];
            var $el = $(".rooms_list");
            $.each(self.rooms, function(r) {
                self.room_ids.push(self.rooms[r]['id']);
                $el.append($("<option></option>")
                        .attr("value", self.rooms[r]['id']).text(self.rooms[r]['name']));
            });

            self.users = JSON.parse(result)[1];
            $el = $(".modal_created_by");
            $.each(self.users, function(u) {
                self.user_ids.push(self.users[u]['id']);
                $el.append($("<option></option>")
                                    .attr("value", self.users[u]['id']).text(self.users[u]['name']));
            });

            self.uid = JSON.parse(result)[2];
            var patients = JSON.parse(result)[3];
            // var $patient_el = $(".patient_list");
            $.each(patients, function(p) {
                /*$patient_el.append($("<option></option>")
                        .attr("value", patients[p]['id']).text(patients[p]['name']));*/
                // self.patient_ids.push(self.patients[p]['id']);
                self.patients[patients[p]['id']] = patients[p];
                if(patients[p]['mobile']){
                    self.phone_no.push({label:patients[p]['mobile'], value:patients[p]['id']});
                }
                if(patients[p]['qid']){
                    self.qid.push({label:patients[p]['qid'], value:patients[p]['id']});
                }
                self.pat_ids.push({label:patients[p]['patient_id'], value:patients[p]['id']});
                self.pat_names.push({label:patients[p]['name'], value:patients[p]['id']});
            });
        }});

        return this._super.apply(this, arguments);
    },

    get_options: function (d, m, y, states, resource_ids) {
        var self = this;

        rpc.query({
            model: 'appointments.calendar',
            method: 'find_appointments',
            args: [d, m, y, self.view_mode, states, resource_ids]
        }).done(function(result){
            var events = result ? result[0] : [];
            var mintime = "";
            var maxtime = "";
            if(result[1]){
               mintime = result[1][0];
               maxtime = result[1][1];
            }
            if(self.status) {
                for (var state = 0; state < self.status.length; state++) {
                    $('#' + self.status[state]['state'][0]).css('background-color', self.status[state]['color'])
                }
            }
            var temp;
            for (var i=0; i<events.length; i++){
                temp = events[i]['start'];
                if (temp){
                    events[i]['start'] = new Date(
                        temp[2], temp[1], temp[0], temp[3], temp[4]
                    );
                }
                temp = events[i]['end'];
                if (temp){
                    events[i]['end'] = new Date(
                        temp[2], temp[1], temp[0], temp[3], temp[4]
                    );
                }
            }
            // self.events_list = events;
            var options = {
                header: {
                    left: 'prev,today,next',
                    center: 'title',
                    right: 'resourceAgendaDay,month,agendaWeek,agendaDay'
                },
                 buttonText: {
                    today: 'Today',
                    month: 'Month',
                    agendaWeek: 'Week',
                    agendaDay: 'Day'
                 },
                editable: true,
                selectable: true,
                selectHelper: true,
                eventLimit: true, // allow "more" link when too many events
                defaultView: 'resourceAgendaDay',
                slotDuration: "00:15:00",
                minTime: mintime,
                maxTime: maxtime,
                views: {
                  resourceAgendaDay: {
                    type: 'resourceAgenda',
                    duration: {
                      days: 1
                    },
                    buttonText: "Doctor-wise"
                  }
                },
                allDaySlot: false, // Unsupported yet
                // unknownResourceTitle: 'Others',
                resources:  self.resources,
                events: events,

                select: function(startDate, endDate, JsEvent, Event) {
                    var clicked = JsEvent.originalEvent.layerX;
                    var cell_id, res_id = null;

                    if(Event && Event.name == 'resourceAgendaDay'){
                        var dayEls = Event.timeGrid.dayEls;
                        for(var el=0;el<dayEls.length;el++){
                            if(clicked > dayEls[el].offsetLeft &&
                                clicked < dayEls[el].offsetLeft+dayEls[el].offsetWidth){
                                cell_id = dayEls[el].cellIndex;
                                res_id = Event.resources[cell_id-1];
                            }
                        }
                    }

                    res_id = res_id ? res_id.id:res_id;

                    $('.modalPhysician').val(res_id);
                    $('#calendarModal').modal();

                    var def_start = startDate.year() + '-' + (startDate.month() + 1) + '-' +
                        startDate.date() + ' ' + moment((startDate.hour() + ':' + startDate.minute()), "HH:mm").format("h:mm A");
                    $(".app_start input").datetimepicker({
                        defaultDate: def_start,
                        widgetPositioning: {
                            horizontal: 'right',
                            vertical: 'bottom'
                        }
                    });
                    var def_end = endDate.year() + '-' + (endDate.month() + 1) + '-' +
                        endDate.date() + ' ' + moment((endDate.hour() + ':' + endDate.minute()), "HH:mm").format("h:mm A")
                    $(".app_end input").datetimepicker({
                        defaultDate: def_end,
                        widgetPositioning: {
                            horizontal: 'right',
                            vertical: 'bottom'
                        }
                    });
                    if(!$(".app_start input").val()){
                        $(".app_start input").val(def_start);
                    }
                    if(!$(".app_end input").val()){
                        $(".app_end input").val(def_end);
                    }
                    $(".qid").val("");
                    $(".Notes").val("");
                    $('.patient_type').prop('checked',true);
                    $(".patient_phone").val("");
                    $(".patient_ids").val("");

                    // return self._onCreateEvent(moment(startDate.format()), moment(endDate.format()), res_id);
                },
                eventClick: function(calEvent, jsEvent, view) {
                    self._onOpenEvent(calEvent);


                    // change the border color just for fun
                    $(this).css('border-color', 'red');
                },
                eventResize: function(event, delta, revertFunc){
                    if (!confirm("Are you sure about this change in end time?")) {
                        revertFunc();
                    } else {
                        rpc.query({
                            model: 'appointments.calendar',
                            method: 'update_appointment_end',
                            args: [
                                parseInt(event.id),
                                parseInt(delta._data.days),
                                parseInt(delta._data.hours),
                                parseInt(delta._data.minutes)
                            ]
                        });
                    }

                },
                eventDrop: function(event, delta, revertFunc){
                    if (!confirm("Are you sure about this change?")) {
                        revertFunc();
                    } else {
                        rpc.query({
                            model: 'appointments.calendar',
                            method: 'update_appointment',
                            args: [
                                parseInt(event.id),
                                parseInt(delta._data.days),
                                parseInt(delta._data.hours),
                                parseInt(delta._data.minutes)
                            ]
                        });
                    }
                }
            };
            $('#appointments_container').fullCalendar2(options);

            $('.fc-today-button').click(function(){
                self.go_to_current_day();
            });

            $('#appointments_container_sub').datepicker({
                onSelect: function(dateText,dp){
                    self.view_mode = 'resourceAgendaDay';
                    self.current_time = new Date(Date.parse(dateText));
                    $('#appointments_container').fullCalendar2('gotoDate', new Date(Date.parse(dateText)));
                    self.rerender_events();
                }
            });
            return ;
        });
    },

    rerender_events: function () {
        var self = this;
        $('#appointments_container').fullCalendar2( 'removeEvents');
        rpc.query({
            model: 'appointments.calendar',
            method: 'find_appointments',
            args: [
                self.current_time.getDate(),
                parseInt(self.current_time.getMonth())+1,
                self.current_time.getFullYear(),
                self.view_mode,
                self.state_names,
                self.resource_ids
            ]
        }).done(function(result) {
            var events = result ? result[0] : [];
            var temp;
            for (var i = 0; i < events.length; i++) {
                temp = events[i]['start'];
                if (temp) {
                    events[i]['start'] = new Date(
                        temp[2], temp[1], temp[0], temp[3], temp[4]
                    );
                }
                temp = events[i]['end'];
                if (temp) {
                    events[i]['end'] = new Date(
                        temp[2], temp[1], temp[0], temp[3], temp[4]
                    );
                }
            }
            $('#appointments_container').fullCalendar2('addEventSource', events);
         });
    },

    on_click_prev_sub: function(){
        $('#appointments_container_sub').fullCalendar2('prev');
    },
    on_click_next_sub: function(){
        $('#appointments_container_sub').fullCalendar2('next');
    },

    on_resource_day: function(){
        this.view_mode = 'resourceAgendaDay';
        this.rerender_events();
    },
    on_click_month: function(){
        this.view_mode = 'month';
        this.rerender_events();
    },
    on_click_week: function(){
        this.view_mode = 'week';
        this.rerender_events();
    },
    on_click_agenda_day: function(){
        this.view_mode = 'day';
        this.rerender_events();
    },

    update_view_options: function (operator) {
        var view_mode;
        if(this.view_mode == 'resourceAgendaDay'){
            view_mode = 'gotoDate';
            this.current_time.setDate(operators[operator](this.current_time.getDate(), 1));
        }
        else if(this.view_mode == 'month'){
            view_mode = 'gotoMonth';
            this.current_time.setMonth(operators[operator](this.current_time.getMonth(), 1));
        }
        else if(this.view_mode == 'week'){
            view_mode = 'gotoDate';
            this.current_time.setDate(operators[operator](this.current_time.getDate(), 7));
        }
        else if(this.view_mode == 'day'){
            view_mode = 'gotoDate';
            this.current_time.setDate(operators[operator](this.current_time.getDate(), 1));
        }
        return view_mode ? view_mode : 'gotoDate';
    },

    on_prev_day: function(){
        var view_mode = this.update_view_options('-');
        var self = this;

        /*removing and re-rendering events*/
        $('#appointments_container').fullCalendar2( 'removeEvents');
        /*changes view*/
        $('#appointments_container').fullCalendar2(view_mode, this.current_time);

        rpc.query({
            model: 'appointments.calendar',
            method: 'find_appointments',
            args: [
                self.current_time.getDate(),
                parseInt(self.current_time.getMonth())+1,
                self.current_time.getFullYear(),
                self.view_mode,
                self.state_names,
                self.resource_ids
            ]
        }).done(function(result) {
            var events = result ? result[0] : [];

            var temp;
            for (var i = 0; i < events.length; i++) {
                temp = events[i]['start'];
                if (temp) {
                    events[i]['start'] = new Date(
                        temp[2], temp[1], temp[0], temp[3], temp[4]
                    );
                }
                temp = events[i]['end'];
                if (temp) {
                    events[i]['end'] = new Date(
                        temp[2], temp[1], temp[0], temp[3], temp[4]
                    );
                }
            }
            $('#appointments_container').fullCalendar2('addEventSource', events);
        });
    },
    on_next_day: function(){
        var view_mode = this.update_view_options('+');

        /*removing and re-rendering events*/
        $('#appointments_container').fullCalendar2( 'removeEvents');
        /*changes view*/
        $('#appointments_container').fullCalendar2(view_mode, this.current_time);
        var self = this;
        rpc.query({
            model: 'appointments.calendar',
            method: 'find_appointments',
            args: [
                self.current_time.getDate(),
                parseInt(self.current_time.getMonth())+1,
                self.current_time.getFullYear(),
                self.view_mode,
                self.state_names,
                self.resource_ids
            ]
        }).done(function(result) {
            var events = result ? result[0] : [];

            var temp;
            for (var i = 0; i < events.length; i++) {
                temp = events[i]['start'];
                if (temp) {
                    events[i]['start'] = new Date(
                        temp[2], temp[1], temp[0], temp[3], temp[4]
                    );
                }
                temp = events[i]['end'];
                if (temp) {
                    events[i]['end'] = new Date(
                        temp[2], temp[1], temp[0], temp[3], temp[4]
                    );
                }
            }
            $('#appointments_container').fullCalendar2('addEventSource', events);
        });
    },

    start: function() {
        var self = this;
        var date = new Date();
        var d = date.getDate();
        var m = date.getMonth();
        var y = date.getFullYear();

        return this._super().then(function() {
            self.update_cp();
            self.update_calendar(d, m, y);
        });
    },
    update_calendar: function(d, m, y){
        var self = this;
        self.get_options(d, parseInt(m)+1, y, this.state_names, this.resource_ids);
    },
   /* _onCreateEvent: function(start, end, resource){
        /!*creating new event*!/
        var self = this;
        return rpc.query({
            model: 'appointments.calendar',
            method: 'get_formview_id',
            //The event can be called by a view that can have another context than the default one.
            args: []
        }).then(function (viewId) {
            self.do_action({
                type:'ir.actions.act_window',
                res_model: 'medical.appointment',
                views: [[viewId || false, 'form']],
                target: 'new',
                context: {
                    default_appointment_sdate: start,
                    default_doctor: resource ? parseInt(resource) : null
                }
            }).then(function () {
                $('button.close').click(function (ev) {
                    var d = self.current_time.getDate();
                    var m = self.current_time.getMonth();
                    var y = self.current_time.getFullYear();
                    $('#appointments_container').fullCalendar2('destroy');
                    self.get_options(d, parseInt(m)+1, y, self.state_names, self.resource_ids);
                });
                $('.o_form_button_cancel').click(function (ev) {
                    var d = self.current_time.getDate();
                    var d = self.current_time.getDate();
                    var m = self.current_time.getMonth();
                    var y = self.current_time.getFullYear();
                    $('#appointments_container').fullCalendar2('destroy');
                    self.get_options(d, parseInt(m)+1, y, self.state_names, self.resource_ids);
                });
            });
        });
    },*/
    _onOpenEvent: function (event) {
        /*opening existing event*/
        var self = this;
        var res_id = event ? event.id : false;
        res_id = res_id ? parseInt(res_id) : null;

        rpc.query({
            model: 'appointments.calendar',
            method: 'get_formview_id',
            //The event can be called by a view that can have another context than the default one.
            args: []
        }).then(function (viewId) {
            self.do_action({
                type:'ir.actions.act_window',
                res_id: res_id,
                res_model: event.model ? event.model:'sale.order',
                views: [[viewId || false, 'form']],
                target: 'current',
                context: event.context || self.context,
            });
        });
        return;
    },

    update_cp: function() {
        this.set("title", this.title);
        var breadcrumbs = this.action_manager && this.action_manager.get_breadcrumbs() || [{
                title: this.title,
                action: this
        }];
        this.update_control_panel({
            breadcrumbs: breadcrumbs,
            search_view_hidden: true
        }, {
            clear: true
        });
       /* $('.o_control_panel').css({'height':'53px', 'text-align': 'center'});*/
    }
});

core.action_registry.add('calendar_appointments', AppointmentsToday);

return AppointmentsToday;
});

odoo.define('calendar_resource_view.time_picker', function(require){
    "use_strict";

    var BasicController = require('web.BasicController');
    var Dialog = require('web.Dialog');
    var core = require('web.core');

    BasicController.include({
        canBeDiscarded: function (recordID) {
            if (!this.model.isDirty(recordID || this.handle)) {
                return $.when(false);
            }
            if(this.renderer.activeSettingTab == 'calendar_resource_view'){
                return $.when(false);
            }
            var message = core._t("The record has been modified, your changes will be discarded. Do you want to proceed?");
            var def = $.Deferred();
            var dialog = Dialog.confirm(this, message, {
                title: core._t("Warning"),
                confirm_callback: def.resolve.bind(def, true),
                cancel_callback: def.reject.bind(def),
            });
            dialog.on('closed', def, def.reject);
            return def;
        }
    });
});

odoo.define('calendar_resource_view.time_picker_add_exception', function(require){
    "use_strict";

    var BasicModel = require('web.BasicModel');

    BasicModel.include({
       _applyChange: function (recordID, changes, options) {
            var self = this;
            var record = this.localData[recordID];
            var field;
            var defs = [];
            options = options || {};
            record._changes = record._changes || {};
            if (!options.doNotSetDirty) {
                record._isDirty = true;
            }
            var initialData = {};
            this._visitChildren(record, function (elem) {
                initialData[elem.id] = $.extend(true, {}, _.pick(elem, 'data', '_changes'));
            });

            // apply changes to local data
            for (var fieldName in changes) {
                field = record.fields[fieldName];
                if (field.type === 'one2many' || field.type === 'many2many') {
                    defs.push(this._applyX2ManyChange(record, fieldName, changes[fieldName], options.viewType));
                } else if (field.type === 'many2one' || field.type === 'reference') {
                    defs.push(this._applyX2OneChange(record, fieldName, changes[fieldName]));
                } else {
                    record._changes[fieldName] = changes[fieldName];
                }
            }

            if (options.notifyChange === false) {
                return $.Deferred().resolve(_.keys(changes));
            }

            return $.when.apply($, defs).then(function () {
                var onChangeFields = []; // the fields that have changed and that have an on_change
                for (var fieldName in changes) {
                    field = record.fields[fieldName];
                    if (field.onChange) {
                        var isX2Many = field.type === 'one2many' || field.type === 'many2many';
                        if (!isX2Many || (self._isX2ManyValid(record._changes[fieldName] || record.data[fieldName]))) {
                            onChangeFields.push(fieldName);
                        }
                    }
                }
                var onchangeDef = $.Deferred();
                if (onChangeFields.length) {
                    self._performOnChange(record, onChangeFields, options.viewType)
                        .then(function (result) {
                            delete record._warning;
                            onchangeDef.resolve(_.keys(changes).concat(Object.keys(result && result.value || {})));
                        }).fail(function () {
                            self._visitChildren(record, function (elem) {
                                _.extend(elem, initialData[elem.id]);
                            });
                            onchangeDef.resolve({});
                        });
                } else {
                    onchangeDef = $.Deferred().resolve(_.keys(changes));
                }
                return onchangeDef.then(function (fieldNames) {
                    _.each(fieldNames, function (name) {
                        var excpet = {};
                        if(record && record['fieldsInfo'] && record['fieldsInfo']['form'] && record['fieldsInfo']['form'][name]){
                            var curr_el = record['fieldsInfo']['form'][name];
                            if(curr_el['widget'] == 'timepicker' ||
                                curr_el['widget'] == 'colorpicker'){
                                excpet[name] = true;
                            }
                        }
                        if (record._changes && record._changes[name] === record.data[name]) {
                            delete record._changes[name];
                            record._isDirty = !_.isEmpty(record._changes);
                        }
                        else if(record._changes && record._changes[name] != record.data[name]){
                            if(excpet[name] && excpet[name] == true){
                                //delete record._changes[name];
                                fieldNames.splice( fieldNames.indexOf(name), 1 );
                                record._isDirty = !_.isEmpty(fieldNames);
                            }
                        }
                    });
                    return self._fetchSpecialData(record).then(function (fieldNames2) {
                        // Return the names of the fields that changed (onchange or
                        // associated special data change)
                        return _.union(fieldNames, fieldNames2);
                    });
                });
            });
        }
    });

});
