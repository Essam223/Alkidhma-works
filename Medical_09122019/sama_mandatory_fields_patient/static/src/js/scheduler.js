odoo.define('sama_mandatory_fields_patient.scheduler', function(require) {
    "use strict";
    var CalendarQuickCreate2 = require('calendar_scheduler.CalendarQuickCreate2');
    CalendarQuickCreate2.include({
        _quickAdd: function (code) {
            var new_valss = {
                patient_state: $('select.patient_stat').val(),
                patient_name: $('.patient_name').val(),
                patient_phone: $('.patient_phone').val(),
                qid: $('.qid').val(),
                sex: $('select.gender').val(),
                nationality_id: $('select.nationality_id').val(),
                dob: $('.dob').val(),
            };
//            console.log(new_valss['nationality_id'], "--------------------natioanlity")
            if (new_valss['patient_state'] == 'walkin'){
                var new_missing_values = false;
                if (!new_valss['patient_name']) {
                    new_missing_values = true;
                    $('.patient_name').css('border-color', 'red');
                }
                if (!new_valss['patient_phone']) {
                    new_missing_values = true;
                    $('.patient_phone').css('border-color', 'red');
                }
                if (!new_valss['qid']) {
                    new_missing_values = true;
                    $('.qid').css('border-color', 'red');
                }
                if (!new_valss['sex']) {
                    new_missing_values = true;
                    $('.gender').css('outline', '1px solid');
                    $('.gender').css('outline-color', 'red');
                }
                if (!new_valss['nationality_id']) {
                    new_missing_values = true;
                    $('.nationality_id').css('outline', '1px solid');
                    $('.nationality_id').css('outline-color', 'red');
                }
                if (!new_valss['dob']) {
                    new_missing_values = true;
                    $('.dob').css('border-color', 'red');
                }
                if (new_valss['patient_name']) {
                    $('.patient_name').css('border-color', 'lightgrey');
                }
                if (new_valss['patient_phone']) {
                    $('.patient_phone').css('border-color', 'lightgrey');
                }
                if (new_valss['qid']) {
                    $('.qid').css('border-color', 'lightgrey');
                }
                if (new_valss['sex']) {
                    $('.gender').css('outline-color', 'lightgrey');
                }
                if (new_valss['nationality_id']) {
                    $('.nationality_id').css('outline-color', 'lightgrey');
                }
                if (new_valss['dob']) {
                    $('.dob').css('border-color', 'lightgrey');
                }
                if (new_missing_values === true) {
                    $('.required_field_warning').css({
                        'display': 'block'
                    });
                }
                else {
                    return this._super(code);
                }
            }
            else {
                    return this._super(code);
                }
        },
    });
});
