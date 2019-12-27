odoo.define('calendar_scheduler.CalendarQuickCreate2', function (require) {
"use strict";

var core = require('web.core');
var Dialog = require('web.Dialog');
var rpc = require('web.rpc');
var session = require('web.session');
var _t = core._t;
var QWeb = core.qweb;

function dateToServer (date) {
    return date.clone().utc().locale('en').format('YYYY-MM-DD HH:mm:ss');
}

/**
 * Quick creation view.
 *
 * Triggers a single event "added" with a single parameter "name", which is the
 * name entered by the user
 *
 * @class
 * @type {*}
 */
var QuickCreate3 = Dialog.extend({
	init: function (parent, options) {
		this.parent = parent;

        this._super(parent, {
            title: "Patient Selection",
            size: 'smaller',
            buttons: [{text: _t("Cancel"),
                       close: true, click: function () {
                        parent.clearAll();
                     }}
            ],
            $content: QWeb.render('CalendarView2.pat_list_wiz', {
                options: options,
            })
        });
    },
    start: function () {
        this._super();
    }
});

var QuickCreate2 = Dialog.extend({
    events: _.extend({}, Dialog.events, {
        'keyup input': '_onkeyup',
        'change .patient_type': 'change_patient_type',
        'change .followup_app': 'onchange_followup_app',
        'change .modal_start_time': 'get_followup_app_start',
        'change .modal_end_time': 'onchange_app_end',
        'change select.staff': 'get_followup_modalPhysician',
        'change .dob': 'onchange_dob',
    }),

    /**
     * @constructor
     * @param {Widget} parent
     * @param {Object} buttons
     * @param {Object} options
     * @param {Object} dataTemplate
     * @param {Object} dataCalendar
     */
    init: function (parent, buttons, options, dataTemplate, dataCalendar) {
        this._buttons = buttons || false;
        this.options = options;

        // Can hold data pre-set from where you clicked on agenda
        this.dataTemplate = dataTemplate || {};
        this.dataCalendar = dataCalendar;

        var self = this;

		function n(n){
            return n > 9 ? "" + n: "0" + n;
        }
		options.time_slots = parent.renderer.time_slots;

		options.start = n(dataCalendar.start.hour()) + ':' + n(dataCalendar.start.minutes());
		options.end = n(dataCalendar.end.hour()) + ':' + n(dataCalendar.end.minutes());

		options.staff = parent.renderer.doctors;
		options.nationality_ids = parent.renderer.nationality_ids;
		options.rooms = parent.renderer.rooms_list;

		var resource_vals = dataCalendar.resourceId ? dataCalendar.resourceId.split('_') : [false];
        if (resource_vals[0] == 'doctor') {
            options.doctor = dataCalendar.resourceId;
            options.room_id = false;
        } else if (resource_vals[0] == 'room') {
            options.room_id = dataCalendar.resourceId;
            options.doctor = false;
        }
        else {
            options.doctor = parseInt(dataCalendar.resourceId);
        }

		this.patients = parent.renderer.patients ? parent.renderer.patients : [];
        this.phone_no = parent.renderer.phone_no ? parent.renderer.phone_no : [];
        this.qid = parent.renderer.qid ? parent.renderer.qid : [];
        this.pat_names = parent.renderer.pat_names ? parent.renderer.pat_names : [];
        this.pat_ids = parent.renderer.pat_ids ? parent.renderer.pat_ids : [];

		var patients = parent.renderer.patients ? parent.renderer.patients : {};
		var self = this;

        this._super(parent, {
            title: this._getTitle(),
            size: 'large',
            buttons: this._buttons ? [
                {text: _t("Create"),
                 classes: 'btn-primary scheduler_create',
                  click: function () {
                    if (!self._quickAdd(dataCalendar)) {
                        self.focus();
                    }
                }},{text: _t("Clear"),
                 classes: 'scheduler_edit',
                  click: function () {
                    self.clearAll();
                }},
//                {text: _t("Edit"),
//                 classes: 'scheduler_edit',
//                 click: function () {
//                    dataCalendar.disableQuickCreate = true;
//                    dataCalendar.title = self.$('input').val().trim();
//                    dataCalendar.on_save = self.destroy.bind(self);
//                    self.trigger_up('openCreate', dataCalendar);
//                }},
                {text: _t("Cancel"),
                 classes: 'scheduler_cancel',
                 close: true},
            ] : [],
            $content: QWeb.render('CalendarView2.quick_create', {
                widget: this,
                options: options
            })
        });
    },
    start: function () {
        this._super();
		var self = this;
		self.pat_list_all = [];
		self.pat_list = [];
		self.search_status = "";
        function split(val) {
            return val.split(/,\s*/);
        }
        function extractLast(term) {
            return split(term).pop();
        }

        this.$input = this.$('input').keydown(function enterHandler (e) {
            self.search_status = "pending";
        });

        this.$input = this.$('input').on('textInput', e => {
            var keycode  = e.originalEvent.data.charCodeAt(0);
            self.search_status = "pending";
            var currentTarget = $(e.currentTarget);

            if (keycode === $.ui.keyCode.SPACE && $('input.patient_type').prop("checked") == true) {
                self.search_status = '';
                switch (currentTarget.attr('class')) {
                    case 'patient_phone': self.keydown_phone(); break;
                    case 'patient_name': self.keydown_name(); break;
                    case 'qid': self.keydown_qid(); break;
                    case 'patient_ids': self.keydown_patient_ids(); break;
                    default: break;
                };
            }
        });
        this.$input.on('change', function enterHandler (e) {
            if ($('input.patient_type').prop("checked") == true &&
                    self.search_status == 'pending') {
                self.search_status = "";
                switch ($(this).attr('class')) {
                    case 'patient_phone': self.keydown_phone(); break;
                    case 'patient_name': self.keydown_name(); break;
                    case 'qid': self.keydown_qid(); break;
                    case 'patient_ids': self.keydown_patient_ids(); break;
                    default: break;
                };
            }
        });
        this.$('.staff,.patient_stat, select.room_id, select.nationality_id').select2({
            placeholder: 'Select',
			allowClear: true
        });
        this.$(".dob").datepicker();
        this.$('input.patient_phone').val('974');
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    clearAll: function () {
        this.$("input,textarea").val('');
        this.$("select.gender").val('');
        this.$("select.nationality_id").val('');
        this.$("select.nationality_id").trigger('change');
        this.$("select.room_id").val('');
        this.$("select.room_id").trigger('change');
        this.$("input.urgent_app").removeAttr('checked');
        this.$("input.followup_app").removeAttr('checked');
        this.patient_rec = false;
    },
    focus: function () {
        this.$('.patient_name').focus();
    },
    keydown_phone: function () {
        this.autocomplete_method(
            '.patient_phone',
            'mobile'
        );
    },
    keydown_name: function () {
        this.autocomplete_method(
            '.patient_name',
            'patient_name'
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
    onchange_dob: function () {
        if ($('input.patient_type').prop("checked") == true) {
            $('.dob').val((this.patient_rec ? this.patient_rec.dob : '' ));
        }
    },
    patient_by_file: function(patient){
//        var patient = this.patients[p_id];
        $('.patient_list').val(patient.id);
        $('.patient_name').val(patient.name ? patient.name : patient.patient_name);
        $('.qid').val(patient.qid ? patient.qid : null);
        $('.patient_phone').val(patient.mobile ? patient.mobile: null);
        $('.patient_ids').val(patient.patient_id);
        $('select.gender').val(patient.sex);
//        $('select.gender').trigger('change');
        $('.dob').val(patient.dob ? patient.dob : '');
        $('select.nationality_id').val('');
        $('select.nationality_id').val(patient.nationality_id ? patient.nationality_id[0] : '');
        $('select.nationality_id').trigger('change');
        this.patient_rec = patient;
        $('select.gender').attr('disabled', true);
        $('select.nationality_id').attr('disabled', true);
//        $('.dob').attr('readonly', true);
    },
    /*onchange_patient: function(p_id){
        var patient = this.patients[p_id];
        $('.patient_list').val(patient.id);
        $('.patient_name').val(patient.name);
        $('.qid').val(patient.qid);
        $('.patient_phone').val(patient.mobile);
        $('.patient_ids').val(patient.patient_id);
        $('select.gender').val(patient.sex);
//        $('select.gender').trigger('change');
        $('.dob').val(patient.dob);
        $('select.nationality_id').val('');
        $('select.nationality_id').val(patient.nationality_id);
        $('select.nationality_id').trigger('change');
        this.patient_rec = patient;
        $('select.gender').attr('disabled', true);
        $('select.nationality_id').attr('disabled', true);
//        $('.dob').attr('readonly', true);
    },*/
    autocomplete_method: function (selector, key) {
        var self = this;
        function split(val) {
            return val.split(/,\s*/);
        }

        if (key == 'pat_ids') {
            var search_val = $(selector).val().trim();
            return rpc.query({
                model: 'medical.patient',
                method: 'search_read',
                domain: [['patient_id', '=', search_val], ['company_id','=', session.company_id]],
                fields: [
                    'patient_name', 'id', 'qid', 'mobile',
                    'patient_id', 'sex', 'dob',
                    'nationality_id',
                ]
            }).then(function (result) {
                if (result.length > 0) {
                    self.patient_by_file(result[0]);
                    $(selector).css('border', '1px solid #aaa');
                    $('.qid').css('border', '1px solid #aaa');
                    $('.patient_name').css('border', '1px solid #aaa');
                    $('.patient_phone').css('border', '1px solid #aaa');
                }
                else {
                    $(selector).val('');
                    $(selector).css('border', '1px solid red');
                    self.clearAll();
                }
            });
        }
        else if (key == 'patient_name') {
            var search_val = $(selector).val().trim();
            $(selector).val(search_val);

            self.pat_list = [];
            self.pat_list_all = [];
            $(selector).autocomplete({
                select: function (event, ui) {
                    var terms = split(this.value);
                    // remove the current input
                    terms.pop();
                    // add the selected item
                    terms.push(ui.item.label);
                    this.value = terms;

                    var patient = null;
                    if (self.pat_list_all[ui.item.value - 1]) {
	                    self.patient_by_file(self.pat_list_all[ui.item.value - 1]);
	                    patient = self.pat_list_all[ui.item.value - 1].id;
	                    $(this).css('border', '1px solid #aaa');
	                    $(selector).autocomplete('destroy');
                    }

                    var doctor_id = $('select.staff').val() ? parseInt($('select.staff').val().split('_')[1]) : false;
                    if (doctor_id == false) {
                        alert("Select a doctor first !");
                        return;
                    }
                    self.followup_function(patient,
                                           self.dataCalendar.start,
                                           doctor_id,
                                           'New')
					self.pat_list_all = [];
					self.pat_list = [];
					search_val = false;
//
                    return false;
                },
                source: function (request, response) {
                    self.pat_list = [];
                    rpc.query({
                        model: 'medical.patient',
                        method: 'search_read',
                        domain: [[key, 'ilike', search_val], ['company_id','=', session.company_id]],
                        fields: [
                            'patient_name', 'id', 'qid', 'mobile',
                            'patient_id', 'sex', 'dob',
                            'nationality_id',
                        ]
                    }).then(function (result) {
                        if (result) {
                            self.pat_list_all = result;
                            for (var p=0;p<result.length;p++) {
                                self.pat_list.push(
                                    {label:result[p][key], value:p+1});
                            }

                            response(self.pat_list);
                        }
                        else {
                            $(selector).val('');
                            $(selector).css('border', '1px solid red');
                            self.clearAll();
                        }
                    });
                },
                change: function (event, ui) {
                    if (ui.item) {
                        $(this).css('border', '1px solid black');
                    }
                    else {
                        $(this).val('');
                        $(this).css('border', '1px solid red');
                        self.clearAll();
                    }
                    $(selector).autocomplete('destroy');
                }
            });
        }
        else {
            /*case for phone number, qid
            i.e, there may be multiple records with same value*/
            var search_val = $(selector).val().trim();

            rpc.query({
                model: 'medical.patient',
                method: 'search_read',
                domain: [[key, '=', search_val], ['company_id','=', session.company_id]],
                fields: [
                    'patient_name', 'id', 'qid', 'mobile',
                    'patient_id', 'sex', 'dob',
                    'nationality_id',
                ]
            }).then(function (result) {
                if (result.length > 1) {
                    var quick = new QuickCreate3(self, result);
                    quick.open();
                    quick.$modal.find('button.close').css('right', '20px');
                    quick.$modal.find('button.close').click(function () {
                        self.clearAll();
                    });
                    $('.patient_body tr').click(function () {
                        var p_selected = $(this).attr('id') ? parseInt($(this).attr('id')) : false;
                        if (!p_selected) {return;}
                        self.patient_by_file(result[p_selected - 1]);
                        $(selector).css('border', '1px solid #aaa');
                        $('.qid').css('border', '1px solid #aaa');
                        $('.patient_name').css('border', '1px solid #aaa');
                        $('.patient_phone').css('border', '1px solid #aaa');
                        quick.close();
                    });
                }
                else if (result.length == 1) {
                    self.patient_by_file(result[0]);
                    $(selector).css('border', '1px solid #aaa');
                    $('.qid').css('border', '1px solid #aaa');
                    $('.patient_name').css('border', '1px solid #aaa');
                    $('.patient_phone').css('border', '1px solid #aaa');
                }
                else {
                    $(selector).val('');
                    $(selector).css('border', '1px solid red');
                    self.clearAll();
                }
            });
        }



//        function split(val) {
//            return val.split(/,\s*/);
//        }
//        function extractLast(term) {
//            return split(term).pop();
//        }
        /*$(el).autocomplete({
            select: function (event, ui) {
                var terms = split(this.value);
                // remove the current input
                terms.pop();
                // add the selected item
                terms.push(ui.item.label);
                this.value = terms;
                self.onchange_patient(ui.item.value);
                var patient =  ui.item.value;
                var doctor_id = $('select.staff').val() ? parseInt($('select.staff').val().split('_')[1]) : false;
                if (doctor_id == false) {
                    alert("Select a doctor first !");
                    return;
                }
				self.followup_function(patient,
				                       self.dataCalendar.start,
				                       doctor_id,
				                       'New')
                return false;
            },
            source: function (request, response) {
                // delegate back to autocomplete, but extract the last term
                if ($('input.patient_type').prop("checked") == true) {
                    var res = $.ui.autocomplete.filter(
                        self[key], extractLast(request.term));
                    if (el== '.patient_ids' && key=='pat_ids'){
                        if(res.length==1){response(res);}
                    }
                    else{
                        response(res);
                    }
                }
                else {
                    response([]);
                }
            },
            change: function (event, ui) {
                if ($('input.patient_type').prop("checked") == true) {
	                var el_class = $(this).attr('class').replace(
	                    'ui-autocomplete-input', '');
	                el_class = el_class.trim();
	                var new_val = '';
	                if (ui.item) {
	                    new_val = ui.item.label;
	                }
	                else if (self.patient_rec) {
	                    new_val = self.findPatientData(el_class);
	                }
	                $(this).val(new_val);
                }
            }
        });*/
    },/*
    findPatientData: function (key) {
        var result = "";
        switch (key) {
            case 'patient_name': result = this.patient_rec.name; break;
            case 'patient_ids': result = this.patient_rec.patient_id; break;
            case 'patient_phone': result = this.patient_rec.mobile; break;
            case 'qid': result = this.patient_rec.qid; break;
            default: break;
        };
        return result;
    },*/
    get_followup_modalPhysician: function () {
        var doctor_id = $('select.staff').val() ? parseInt($('select.staff').val().split('_')[1]) : false;
        if (doctor_id == false) {
	        alert("Select a doctor first !");
            return;
        }
        var patient =  $('.patient_list').val();
        this.followup_function(patient,
                               this.dataCalendar.start,
                               doctor_id,
                               'New')
	},
    onchange_app_end: function () {
        this.dataCalendar.end.set({
            'hour': parseInt($('.modal_end_time').val().split(':')[0]),
            'minute': parseInt($('.modal_end_time').val().split(':')[1])
        });
    },
    get_followup_app_start: function () {
        var appointment_sdate =  $('.modal_start_time').val();
        this.dataCalendar.start.set({
            'hour': parseInt(appointment_sdate.split(':')[0]),
            'minutes': parseInt(appointment_sdate.split(':')[1])
        });
        this.dataCalendar.end.set({
            'hour': parseInt(appointment_sdate.split(':')[0]),
            'minutes': parseInt(appointment_sdate.split(':')[1])
        });
        this.dataCalendar.end.add(15, 'minutes');

        var end_date = this.dataCalendar.end.format('HH:mm');
        $('.modal_end_time').val(end_date);

        var patient =  $('.patient_list').val();

		var doctor_id = $('select.staff').val() ? parseInt($('select.staff').val().split('_')[1]) : false;
        if (doctor_id == false) {
            alert("Select a doctor first !");
            return;
        }
        this.followup_function(patient,
                               this.dataCalendar.start,
                               doctor_id,
                               'New')
    },
    onchange_followup_app: function () {
        if($(".followup_app").prop("checked")== true){
            $('.followup_app').prop('checked',false);
            alert("You cant make this Appointment Followup");
        }

    },
    change_patient_type: function () {
        var checked = $('input.patient_type').prop("checked");
        if (checked == true) {
            $('.box.patient').css('visibility', 'visible');
            $('.patient_ids').val('');
            $('.patient_name').val('');
            $('.patient_list').val('');
            $('.patient_phone').val('974');
            $('.qid').val('');
            $('.dob').val('');
            $('select.nationality_id').val('');
            $('select.nationality_id').trigger('change');
            $('select.gender').val('');

//            $('select.gender').trigger('change');

			$('select.gender').attr('disabled', true);
			$('select.nationality_id').attr('disabled', true);
			this.patient_rec = null;
//			$('.dob').attr('readonly', true);
//			$('.patient_phone').attr('readonly', true);
//			$('.qid').attr('readonly', true);
//			$('select.nationality_id').attr('readonly', true);
//			$('select.gender').attr('readonly', true);
        }
        else{
            $('.patient_ids').val('');
            $('.patient_name').val('');
            $('.patient_list').val('');
            $('.patient_phone').val('974');
            $('.qid').val('');
            $('.dob').val('');
            $('select.nationality_id').val('');
            $('select.nationality_id').trigger('change');
            $('select.gender').val('');
//            $('select.gender').trigger('change');
            $('.box.patient').css('visibility', 'hidden');

			$('select.gender').attr('disabled', false);
            $('select.nationality_id').attr('disabled', false);
            $('.dob').attr('readonly', false);
            this.patient_rec = null;
//            $('.patient_ids').attr('readonly', false);
//            $('.patient_phone').attr('readonly', false);
//            $('.qid').attr('readonly', false);
//            $('select.nationality_id').attr('readonly', false);
//            $('select.gender').attr('readonly', false);
        }
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

	followup_function: function(patient, appointment_sdate, doctor, name){
		var new_date = dateToServer(appointment_sdate);

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
//            alert(message);
        });
    },
    /**
     * @returns {string}
     */
    _getTitle: function () {
        var parent = this.getParent();
        if (_.isUndefined(parent)) {
            return _t("Mark Booking/ Visit");
        }
        var title = (_.isUndefined(parent.field_widget)) ?
                (parent.title || parent.string || parent.name) :
                (parent.field_widget.string || parent.field_widget.name || '');
        return _t("Mark Booking/ Visit: ") + title;
    },
    /**
     * Gathers data from the quick create dialog a launch quick_create(data) method
     */
    _quickAdd: function (dataCalendar) {
        if (dataCalendar.start >= dataCalendar.end) {
            alert("Appointment start time should be before end time.")
            return false;
        }
        dataCalendar = $.extend({}, this.dataTemplate, dataCalendar);

		var self = this, patient = false;

        if ($('input.patient_type').prop("checked") == true) {
            patient = parseInt($('.patient_list').val());
        }
        var doctor_id = $('select.staff').val() ? parseInt($('select.staff').val().split('_')[1]) : false;
        var room_data = $('select.room_id').val() ? parseInt($('select.room_id').val().split('_')[1]) : false;

        var vals = {
            is_registered : $('input.patient_type').prop("checked"),
            appointment_sdate: dataCalendar.start.clone(),
            appointment_edate: dataCalendar.end.clone(),
            patient_name: $('.patient_name').val(),
            patient_state: $('select.patient_stat').val(),
            patient_phone: $('.patient_phone').val(),
            sex: $('select.gender').val(),
            dob: $('.dob').val() ? $('.dob').val() : false,
            nationality_id: $('select.nationality_id').val(),
            qid: $('.qid').val(),
            doctor: doctor_id ? doctor_id : null,
            room_id: room_data ? room_data : null,
            urgency: $('.urgent_app').prop("checked"),
            followup: $('.followup_app').prop("checked"),
            comments: $('input.notes').val(),
        };

        var missing_values = false;
        if (vals['is_registered'] === false) {
            if (!vals['patient_name']) {
                missing_values = true;
                $('.patient_name').css('border-color', 'red');
            }
        }
        else {
	        if (patient) {
	            vals['patient'] = patient;
	            console.log("have patient");
	        } else {
	            missing_values = true;
	            $('.patient_name').css('border-color', 'red');
	        }
        }
        if (!vals['doctor']) {
            missing_values = true;
            $('select.staff').css('border-color', 'red');
        }
        if (!vals['appointment_sdate']) {
            missing_values = true;
            $('.app_start input').css('border-color', 'red');
        }
        if (!vals['patient_state']) {
            missing_values = true;
            $('select.patient_stat').css('border-color', 'red');
        }

        if (missing_values === true) {
            alert("Please fill all the missing values.")
            /*$('.required_field_warning').css({
                'display': 'block'
            });*/
        }
        else {
			return (vals)? this.trigger_up('quickCreate', {
                data: dataCalendar,
                options: this.options,
                create_vals: vals
            }) : false;
        }
    },
    /**
     * @private
     * @param {keyEvent} event
     */
    _onkeyup: function (event) {
        /*the form was submitting on enter key press earlier.
        Now it wont.
        */
        if (event.keyCode === $.ui.keyCode.ESCAPE && this._buttons) {
            this.close();
        }
        /*if (this._flagEnter) {
            return;
        }
        if(event.keyCode === $.ui.keyCode.ENTER) {
            this._flagEnter = true;
            if (!this._quickAdd(this.dataCalendar)){
                this._flagEnter = false;
            }
        } else if (event.keyCode === $.ui.keyCode.ESCAPE && this._buttons) {
            this.close();
        }*/
    },
});

return QuickCreate2;

});
