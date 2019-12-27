odoo.define('pragtech_dental_management.childchart', function(require) {
	"use strict";
var rpc = require('web.rpc');
var Widget = require('web.Widget');

var other_patient_history = new Array();
var treatment_lines = new Array();
var imageMapList = new Array();
var keyList = new Array();
var mapkeystatus;
var selected_treatment = '';
var selected_tooth = '';
var tooth_by_part = 0;
var full_mouth_selected = 0;
var upper_mouth_selected = 0;
var lower_mouth_selected = 0;
var full_mouth_selected_child = 0;
var upper_mouth_selected_child = 0;
var lower_mouth_selected_child = 0;
var checkVal;
var Missing_Tooth = 0;
var Palmer;
var Iso;
var type = '';

var DentalChartView = Widget.extend({
	template : "DentalChildChartView",
    events: {
        'click .view': 'view'
    },
    init : function(parent, options) {
		this._super(parent);
		var self = this;
		self.patient_id = options.params.patient_id;
		self.appointment_id = options.params.appt_id;
		other_patient_history = new Array();
		treatment_lines.length = 0;
		tooth_by_part = 0;
		selected_treatment = ''
		var selected_tooth = '';
		var checkVal = false;
		Missing_Tooth = 0;
		self.type = options.params.type;
		type = self.type;
		if (type == 'palmer') {
			var palmer = {
				'A': 'E-1x',
				'B': 'D-1x',
				'C': 'C-1x',
				'D': 'B-1x',
				'E': 'A-1x',
				'F': 'A-2x',
				'G': 'B-2x',
				'H': 'C-2x',
				'I': 'D-2x',
				'J': 'E-2x',
				'K': 'E-3x',
				'L': 'D-3x',
				'M': 'C-3x',
				'N': 'B-3x',
				'O': 'A-3x',
				'P': 'A-4x',
				'Q': 'B-4x',
				'R': 'C-4x',
				'S': 'D-4x',
				'T': 'E-4x'
			};
			Palmer = palmer;
		}
		if (type == 'iso') {
			var iso = {
				'A': '55',
				'B': '54',
				'C': '53',
				'D': '52',
				'E': '51',
				'F': '61',
				'G': '62',
				'H': '63',
				'I': '64',
				'J': '65',
				'K': '75',
				'L': '74',
				'M': '73',
				'N': '72',
				'O': '71',
				'P': '81',
				'Q': '82',
				'R': '83',
				'S': '84',
				'T': '85'
			};
			Iso = iso;
		}
	},
	decrement_thread : function(selected_surf) {
	    try {
            _.each(selected_surf, function(ss) {
                var prev_cnt = ($('#'+ss).attr('class').split(' ')[3]);
                var new_cnt = String(parseInt(prev_cnt) - 1);
                document.getElementById(ss).classList.remove(prev_cnt);
                document.getElementById(ss).classList.add(new_cnt);
            });
        }
        catch (err) {}
	},
	increment_thread : function(selected_surf) {
	    try {
            _.each(selected_surf, function(ss) {
                var m = $('#' + ss).attr('class').split(' ');
                var prev_cnt = ($('#'+ss).attr('class').split(' ')[3]);
                var new_cnt = String(parseInt(prev_cnt) + 1);
                document.getElementById(ss).classList.remove(prev_cnt);
                document.getElementById(ss).classList.add(new_cnt);
            });
        }
        catch (err) {}
	},
	color_surfaces : function(svg_var, surface_to_color, tooth_id, self_var) {
		_.each(surface_to_color, function(each_surface_to_color) {
			if (each_surface_to_color) {
				var found_surface_to_color = $(svg_var).find("." + tooth_id + "_" + each_surface_to_color);
				$('#' + found_surface_to_color[0].id).attr('fill', 'orange');
				self_var.increment_thread([found_surface_to_color[0].id]);
			}
		});
	},
	add_selection_action : function(selection_ids) {
		_.each(selection_ids, function(each_of_selection_ids) {
			$('#childview_' + String(each_of_selection_ids) + '_top').attr('fill', 'orange');
			$('#childview_' + String(each_of_selection_ids) + '_bottom').attr('fill', 'orange');
			$('#childview_' + String(each_of_selection_ids) + '_left').attr('fill', 'orange');
			$('#childview_' + String(each_of_selection_ids) + '_right').attr('fill', 'orange');
			$('#childview_' + String(each_of_selection_ids) + '_center').attr('fill', 'orange');
		});
	},
	perform_missing_action : function(missing_tooth_ids) {
		_.each(missing_tooth_ids, function(each_of_missing_tooth_ids) {
			// $('#' + String(each_of_missing_tooth_ids)).attr('src', "/pragtech_dental_management/static/src/img/images.png");
			$('#' + String(each_of_missing_tooth_ids)).css('visibility', 'hidden').attr('class', 'blank');
			$('#childview_' + String(each_of_missing_tooth_ids) + '_top').attr('visibility', 'hidden');
			$('#childview_' + String(each_of_missing_tooth_ids) + '_bottom').attr('visibility', 'hidden');
			$('#childview_' + String(each_of_missing_tooth_ids) + '_left').attr('visibility', 'hidden');
			$('#childview_' + String(each_of_missing_tooth_ids) + '_right').attr('visibility', 'hidden');
			$('#childview_' + String(each_of_missing_tooth_ids) + '_center').attr('visibility', 'hidden');
		});
	},
	check_if_tooth_present : function(tooth_id) {
		for (var i = 0; i < treatment_lines.length; i++) {
			if (treatment_lines[i]['tooth_id'] == tooth_id) {
				return 1;
			}
		}
		return 0;
	},
	execute_create : function(attrs, self_var, selected_surface_temp) {
		if (!selected_surface_temp) {
			selected_surface_temp = selected_surface;
		}
		var self = this;
		var tooth_present = 0;
		tooth_present = this.check_if_tooth_present(selected_tooth);
		var record = new Array();
		record['treatments'] = new Array();
		record['tooth_id'] = selected_tooth;
		var surfaces = new Array();
		_.each(selected_surface_temp, function(each_surface) {
			var surface = ($('#'+each_surface).attr('class')).split(' ')[1];
			surfaces.push(surface);
		});
		var d = new Array();
		d = {
			'treatment_id' : selected_treatment['treatment_id'],
			'vals' : surfaces
		};
		var selected_tooth_temp = selected_tooth;
		if (attrs) {
			if (!tooth_present) {
				record['treatments'].push(d);
				treatment_lines.push(record);
				this.put_data(
					self_var, surfaces,
					selected_tooth_temp,
					selected_surface_temp, 'planned',
					false, false,
					false,false,false,0,"draft",
					false,
					session.uid,
					user_name
				);
			} else {
				var treatment_present = 0;
				for (var i = 0; i < treatment_lines.length; i++) {
					if (treatment_lines[i]['tooth_id'] == parseInt(selected_tooth_temp)) {
						for (var each_trts = 0; each_trts < treatment_lines[i]['treatments'].length; each_trts++) {
							if (treatment_lines[i]['treatments'][each_trts].treatment_id == selected_treatment['treatment_id']) {
								treatment_present = 1;
								break;
							}
						}
						if (!treatment_present) {
							var x = treatment_lines;
							treatment_lines[i]['treatments'].push(d);
							var doc_name = self.doctor_name ? self.doctor_name : user_name;
							this.put_data(
								self_var, surfaces,
								selected_tooth_temp,
								selected_surface_temp,
								false, false,
								false, false,
								false, false, 0, "draft",
								false,
								session.uid,
								user_name
							);
						}
					}
				}

			}
		} else {
			if (!tooth_present && !tooth_by_part) {
				record['treatments'].push(d);
				treatment_lines.push(record);
				surfaces.length = 0;
				var doc_name = self.doctor_name ? self.doctor_name : user_name;
				this.put_data(
					self_var, surfaces, selected_tooth_temp,
					false, false, false, false,
					false, false, false, 0, "draft",
					false, session.uid, user_name
				);
			} else {
		        record['treatments'].push(d);
			    treatment_lines.push(record);
			    surfaces.length = 0;
		        selected_tooth_temp = toothmap_id;
				surfaces.push(tid);
				var doc_name = self.doctor_name ? self.doctor_name : user_name;
				this.put_data(self_var, surfaces,
					selected_tooth_temp, '',
					'planned', false, false,
					false, false, false, 0, "draft",
					false,
					session.uid,
					user_name
				);
			}
		}
	},
	write_patient_history : function(self_var, res) {
		var is_prev_record_from_write = false;
		_.each(res, function(each_operation) {

			selected_treatment = {
				'treatment_id' : each_operation['desc']['id'],
				'treatment_name' : each_operation['desc']['name'],
				'action' : each_operation['desc']['action']
			};
			is_prev_record_from_write = false;
			if (each_operation['status'] == 'completed') {
				is_prev_record_from_write = true;
			}
			if (each_operation['status'] == 'in_progress')
				each_operation['status'] = 'in_progress';
			if (each_operation['tooth_id']){
				imageMapList = each_operation['surface'];
				var ts = imageMapList ;
                var tooth_surface = ts.slice(0,-3);
                var surface_chk =((tooth_surface == 'root')||(tooth_surface == 'crown')||(tooth_surface == 'toothcap'));
				if((tooth_surface == 'root')||(tooth_surface == 'crown')||(tooth_surface == 'toothcap')) {
					keyList.push(imageMapList);
					var mapkeystr = keyList +',';
					localStorage.setItem('test', mapkeystr);
				}
				
				self_var.put_data(
					self_var,
					each_operation['surface'].split(' '),
					each_operation['tooth_id'], false,
					each_operation['status'], each_operation['created_date'],
					is_prev_record_from_write, each_operation['other_history'],
					each_operation['dignosis'],each_operation['dignosis_description'],
					each_operation['amount'],
					each_operation['inv_status'],
					each_operation['id'],
					each_operation['dentist'][0], //doctor id
					each_operation['dentist'][1] //doctor name
				);
			}
			else {
				self_var.put_data_full_mouth(
					self_var,
					each_operation.multiple_teeth,
					1,
					selected_treatment,
					each_operation['status'],
					each_operation['surface'],
					each_operation['created_date'],
					is_prev_record_from_write,
					each_operation['other_history'],
					each_operation['dignosis'],
					each_operation['dignosis_description'],
					each_operation['amount'],
					each_operation['inv_status'], //invoice status
					each_operation['id'], //treatment line id
					each_operation['dentist'][0], //doctor id
					each_operation['dentist'][1] // doctor name
				);

			}
		});
		selected_treatment = '';
	},
	childview: function(){
		tooth_by_part = 0;
		var surf = selected_surface;
		var chksurf= surf.slice(0,-3);

		if ((chksurf=='root')||(chksurf=='crown')||(chksurf=='toothcap')){
			selected_surface = [];
		}
		if(!tooth_by_part){
			if (!cont || update) {
				selected_surface.length = 0;
				cont = true;
			} else {
				if (selected_surface[0]) {
					var tooth = (selected_surface[0].split('_'))[1];
					var current_tooth = ((this.id).split('_'))[1];
					if (current_tooth != tooth) {
						for (var i = 0; i < selected_surface.length; i++) {
							$("#" + selected_surface[i]).attr('fill', 'white');
						}
						selected_surface.length = 0;
					}
				}
			}
		}
		var found_selected_operation = self.$el.find('.selected_operation');
		if (found_selected_operation[0]) {
			var op_id = ((found_selected_operation[0].id).split('_'))[1];
			if ($('#status_' + op_id)[0].innerHTML == 'Completed'){
				alert('Cannot update Completed record');
				$('#operation_' + op_id).removeClass('selected_operation');
				return;
			}
			var s = (($("#" + this.id).attr('class')).split(' '))[1];
			if (((this.id).split('_'))[1] == $('#tooth_' + op_id).attr('class')) {
				update = true;
				var surf_old_list = ($('#surface_'+op_id)[0].innerHTML).split(' ');
				var got = 0;
				for (var in_list = 0; in_list < surf_old_list.length; in_list++) {
					if (surf_old_list[in_list] == s) {
						got = 1;
						var index = selected_surface.indexOf(this.id);
						selected_surface.splice(index, 1);
						$('#surface_' + op_id).empty();
						_.each(surf_old_list, function(sol) {
							if (sol != s)
								$('#surface_'+op_id)[0].innerHTML += sol + ' ';
						});
						self.decrement_thread([this.id]);
						break;
					}
				}
				if (got == 0) {
					$('#surface_'+op_id)[0].innerHTML += s + ' ';
					selected_surface.push(this.id);
					self.increment_thread([this.id]);
				}
			} else {
				update = false;
			}
		}
		selected_tooth = ((this.id).split('_'))[1];
		if ($("#" + $(this).attr('id')).attr('fill') == 'white') {
			$("#" + $(this).attr('id')).attr('fill', 'orange');
			var available = selected_surface.indexOf(this.id);
			if(available == -1 && is_tooth_select == false){
				selected_surface.push(this.id);
			}
		} else if (parseInt(($("#" + $(this).attr('id')).attr('class')).split(' ')[3]) == 0){
			is_tooth_select = false
			$("#" + $(this).attr('id')).attr('fill', 'white');
			var index = selected_surface.indexOf(this.id);
			selected_surface.splice(index, 1);
		} else {
			if ($("#" + $(this).attr('id')).attr('fill') == 'orange') {
				$("#" + $(this).attr('id')).attr('fill', 'white');
				is_tooth_select = true;
				var current_tooth_id = this.id.lastIndexOf("_");
				var res = this.id.slice(current_tooth_id, this.id.length);
			} else{
				selected_surface.push(this.id);
			}
		}
	}
});

$(document).ready(function() {
var selected_surface = new Array();
var cont = true;
var update = false;
var selected_tooth = '';
var is_tooth_select = false;
$("input[name$='chartoption']").change(function(event) {
	var checkVal = event.currentTarget.value
	$('#img_child_tooth').addClass("hidden");
	$('#img_adult_tooth').addClass("hidden");
	$('#img_tooth_line').addClass("hidden");
	if(checkVal == "adult") {
		$("div.childteethchart").hide();
		if(! $("div.childteethchart").hasClass("hidden")) {
			$("div.childteethchart").addClass("hidden")
		}
		$("div.teethchartadult").show();
		if($("div.teethchartadult").hasClass("hidden")) {
			$("div.teethchartadult").removeClass("hidden")
		}

		if(! $("#select_full_mouth_child").hasClass("hidden")) {
			$("#select_full_mouth_child").addClass("hidden")
		}
		if($("#select_full_mouth").hasClass("hidden")) {
			$("#select_full_mouth").removeClass("hidden")
		}

		if(! $("#select_upper_mouth_child").hasClass("hidden")) {
			$("#select_upper_mouth_child").addClass("hidden")
		}
		if($("#select_upper_mouth").hasClass("hidden")) {
			$("#select_upper_mouth").removeClass("hidden")
		}

		if(! $("#select_lower_mouth_child").hasClass("hidden")) {
			$("#select_lower_mouth_child").addClass("hidden")
		}
		if($("#select_lower_mouth").hasClass("hidden")) {
			$("#select_lower_mouth").removeClass("hidden")
		}
	}
	if(checkVal == "child"){
		$("div.teethchartadult").hide();
		if(! $("div.teethchartadult").hasClass("hidden")) {
			$("div.teethchartadult").addClass("hidden")
		}
		$("div.childteethchart").show();
		if($("div.childteethchart").hasClass("hidden")) {
			$("div.childteethchart").removeClass("hidden")
		}

		if(! $("#select_full_mouth").hasClass("hidden")) {
			$("#select_full_mouth").addClass("hidden")
		}
		if($("#select_full_mouth_child").hasClass("hidden")) {
			$("#select_full_mouth_child").removeClass("hidden")
		}

		if(! $("#select_upper_mouth").hasClass("hidden")) {
			$("#select_upper_mouth").addClass("hidden")
		}
		if($("#select_upper_mouth_child").hasClass("hidden")) {
			$("#select_upper_mouth_child").removeClass("hidden")
		}

		if(! $("#select_lower_mouth").hasClass("hidden")) {
			$("#select_lower_mouth").addClass("hidden")
		}
		if($("#select_lower_mouth_child").hasClass("hidden")) {
			$("#select_lower_mouth_child").removeClass("hidden")
		}
	}

var $def = $.Deferred();
var self = this;
rpc.query({
    model: 'medical.patient',
    method: 'get_patient_history',
    args: [
    	self.patient_id,
    	self.appointment_id
   ],
}).then(function(patient_history) {
	Missing_Tooth = patient_history[0];
	patient_history.splice(0, 1);
	other_patient_history = patient_history;
	$def.resolve(patient_history);
});
/*self.write_patient_history(self, other_patient_history);*/

if(! $('#svg_child').hasClass('numberupdated')) {
	/*self.write_patient_history(self, other_patient_history);*/
	rpc.query({
		model: 'teeth.code',
		method: 'get_teeth_code',
		args: [this.patient_id],
	}).then(function(res){
		var name = "";
		var j = 0;
		var l = 0;
		for (var i = 0; i < 10; i++) {
			name = "<td width='5px' id='teeth_" + i + "'>" + res[i+32] + "</td>";
			$('#child_upper_teeths').append(name);
			/*$('#child_upper_teeths').parents('.numbering').removeClass('numbering').addClass('childnumberingupper');*/
		}
		for (var i = 19; i > 9; i--) {
			name = "<td width='5px' id='teeth_" + i + "'>" + res[i+32] + "</td>";
			$('#child_lower_teeths').append(name);
			/*$('#child_lower_teeths').parents('.numbering_below').removeClass('numbering_below').addClass('childnumberinglower')*/
		}
	});
	$('#svg_child').addClass('numberupdated');
}

_.each(other_patient_history, function(each_operation) {
    imageMapList = each_operation['surface'];
    var ts = imageMapList ;
    var tooth_surface = ts.slice(0,-3);
    var tempImageMapList = new Array();
    var surface_chk =((tooth_surface == 'root')||(tooth_surface == 'crown')||(tooth_surface == 'toothcap'));
    if ((each_operation.tooth_id) && (!surface_chk)) {
        self.color_surfaces(
        	svg, each_operation['surface'].split(' '),
        	each_operation['tooth_id'], self
        );
    } else if((each_operation.tooth_id) && (surface_chk)) {
    	tempImageMapList.push(imageMapList);
    	var mapkeystr = tempImageMapList +',';
        return;
    } else {
    	if (each_operation['surface'] == 'Full_mouth') {
    		self.add_selection_action(each_operation['multiple_teeth']);
        }
        if ((each_operation['surface']=='Upper_Jaw') || (each_operation['surface']=='Lower_Jaw')) {
            var keystr = '';
            if (each_operation['surface']=='Upper_Jaw') {
            	for ( var i=1; i<10;i++)
                	keystr += ',toothcap_'+i;
            	localStorage.setItem('upperkeys', keystr);
            }
            if (each_operation['surface']=='Lower_Jaw') {
            	for ( var i=11; i<=20;i++)
            		keystr += ',toothcap_'+i;
            	localStorage.setItem('lowerkeys', keystr);
            }
		}
		each_operation.tooth_id = '-';
		if (each_operation['desc']['action'] == 'missing') {
			self.perform_missing_action(each_operation['multiple_teeth']);
		}
	}
});

$("img").click(function() {
	if (!selected_treatment) {
		if ($(this).attr('class') == 'selected_tooth') {
			try {
				(this).removeClass('selected_tooth');
				self.decrement_thread(['childview_' + this.id + '_bottom', 'childview_' + this.id + '_center', 'childview_' + this.id + '_right', 'childview_' + this.id + '_left', 'childview_' + this.id + '_top']);
				if (document.getElementById('childview_' + this.id + '_center').classList[3] == "0")
					$('#childview_' + this.id + '_center').attr('fill', 'white');
				if (document.getElementById('childview_' + this.id + '_right').classList[3] == "0")
					$('#childview_' + this.id + '_right').attr('fill', 'white');
				if (document.getElementById('childview_' + this.id + '_left').classList[3] == "0")
					$('#childview_' + this.id + '_left').attr('fill', 'white');
				$('#childview_' + this.id + '_top').attr('fill', 'white');
				$('#childview_' + this.id + '_bottom').attr('fill', 'white');
				selected_surface.length = 0;
            }
            catch (err) {}
		} else {
			$(this).attr('class', 'selected_tooth');
			$('#childview_' + this.id + '_center').attr('fill', 'orange');
			$('#childview_' + this.id + '_right').attr('fill', 'orange');
			$('#childview_' + this.id + '_left').attr('fill', 'orange');
			$('#childview_' + this.id + '_top').attr('fill', 'orange');
			$('#childview_' + this.id + '_bottom').attr('fill', 'orange');
			self.increment_thread(['childview_' + this.id + '_bottom', 'childview_' + this.id + '_center', 'childview_' + this.id + '_right', 'childview_' + this.id + '_left', 'childview_' + this.id + '_top']);
		}
		return;
	}
	selected_tooth = this.id;
	self.execute_create(false, self, false);
	switch(selected_treatment.action) {
		case 'missing':
			if ($("#" + $(this).attr('id')).attr('class') == "teeth") {
				// $($("#" + $(this).attr('id')).attr('src', "/pragtech_dental_management/static/src/img/images.png").attr('class', 'blank'));
				$($("#" + $(this).attr('id')).attr('class', 'blank'));
				$($("#" + $(this).attr('id'))).css('visibility', 'hidden');
				$("#childview_" + $(this).attr('id') + "_top,#childview_" + $(this).attr('id') + "_left,#childview_" + $(this).attr('id') + "_bottom,#childview_" + $(this).attr('id') + "_right,#childview_" + $(this).attr('id') + "_center").attr('visibility', 'hidden');
			} else {
				$($("#" + $(this).attr('id')).css('visibility', 'visible').attr('class', 'teeth'));
				$("#childview_" + $(this).attr('id') + "_top,#childview_" + $(this).attr('id') + "_left,#childview_" + $(this).attr('id') + "_bottom,#childview_" + $(this).attr('id') + "_right,#childview_" + $(this).attr('id') + "_center").attr('visibility', 'visible');
				for (var op_id = 1; op_id <= operation_id; op_id++) {
					if (self.$('#operation_'+op_id)[0]) {
						var got_op_id = (self.$('#operation_'+op_id)[0].id).substr(10);
						if (parseInt(self.$('#tooth_'+got_op_id)[0].innerHTML) == parseInt(this.id)) {
							var tr = document.getElementById('operation_' + got_op_id);
							var desc_class = $("#desc_" + got_op_id).attr('class');
							tr.parentNode.removeChild(tr);
							for (var index = 0; index < treatment_lines.length; index++) {
								if (treatment_lines[index].teeth_id == this.id) {
									for (var i2 = 0; i2 < treatment_lines[index].values.length; i2++) {
										if (treatment_lines[index].values[i2].categ_id == parseInt(desc_class)) {
											treatment_lines.splice(index, 1);
											operation_id += 1;
											return;
										}
									}
								}
							}
							break;
						}
					}
				}
			}
			break;
		case 'composite':
			break;
		default :
			break;
		};

	});

});

self.$('.jaw').click(function(event) {
	$('input:checkbox[name=mouthselection]').each(function(event) {
		if($(this).is(':checked')) {
			var selected_chkbox =($(this).val());
			var keystr = 'tooth';
			if (selected_chkbox == 'uppermouth_child') {
				for (var i=1; i<11; i++)
					keystr += ',chcap_'+i;
				localStorage.setItem('childupperkeys', keystr);
				upper_mouth_selected_child = 1;
			}
			if (selected_chkbox == 'lowermouth_child') {
				for (var i=11; i<=20; i++)
					keystr += ',chcap_'+i;
				localStorage.setItem('childlowerkeys', keystr);
				lower_mouth_selected_child = 1;
			}
			if (selected_chkbox == 'uppermouth') {
        		for (var i=1; i<17; i++)
        			keystr += ',toothcap_'+i;
        		localStorage.setItem('upperkeys', keystr);
        		upper_mouth_selected = 1;
        	}
        	if (selected_chkbox == 'lowermouth'){
        		for (var i=17; i<=33; i++)
        			keystr += ',toothcap_'+i;
        		localStorage.setItem('lowerkeys', keystr);
        		lower_mouth_selected = 1;
        	}
		}
    });
});
_.each(other_patient_history, function(each_operation) {
    imageMapList = each_operation['surface'];
    var ts = imageMapList ;
    //  var tooth_surface = ts;
    var tooth_surface = ts.slice(0,-3);
    var tempImageMapList = new Array();
    //var tooth_surface = (imageMapList[0].split('_'))[0];

//					//console.log('inside fn call line 458 ts is',ts,tooth_surface);

    var surface_chk =((tooth_surface == 'root')||(tooth_surface == 'crown')||(tooth_surface == 'toothcap'));
    //console.log(each_operation, "checking the surface ",surface_chk);

//                    console.log(tooth_surface, "each_operation", each_operation)
    if ((each_operation.tooth_id) && (!surface_chk)) {
        self.color_surfaces(svg, each_operation['surface'].split(' '),
                              each_operation['tooth_id'], self);
    }
    else if((each_operation.tooth_id) && (surface_chk)) {
        tempImageMapList.push(imageMapList);
        var mapkeystr = tempImageMapList +',';
        return;
    }
    else {
        if (each_operation['surface'] == 'Full_mouth') {
            self.add_selection_action(each_operation['multiple_teeth']);
        }
        if ((each_operation['surface']=='Upper_Jaw') ||
            (each_operation['surface']=='Lower_Jaw')) {
            var keystr = '';
            if (each_operation['surface']=='Upper_Jaw') {
                for ( var i=1; i<17;i++)
                    keystr += ',toothcap_'+i;
                //                                     //console.log('in on load from history',keystr);
                localStorage.setItem('upperkeys', keystr);
            }
            if (each_operation['surface']=='Lower_Jaw') {
                for ( var i=17; i<=32;i++)
                      keystr += ',toothcap_'+i;
//                                console.log("setup keystr", keystr)
                localStorage.setItem('lowerkeys', keystr);
            }
		}
		each_operation.tooth_id = '-';
		if (each_operation['desc']['action'] == 'missing') {
			self.perform_missing_action(each_operation['multiple_teeth']);
		}
    }

});


});
});
