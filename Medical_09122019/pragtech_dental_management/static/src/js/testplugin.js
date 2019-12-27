//odoo.define('pragtech_dental_management.testplugin', function(require){
//'use strict'
//
//$(function() {
// https://stackoverflow.com/questions/41682949/odoo-10-integrate-third-party-js-libraries
//   $('.shifter').shifter({
//        maxShift: 1,
//        switcher: true,
//        responsive: true,
//        speed: 1000,
//    });
//
//this.$el.find('.shifter').shifter()
//
////so instead of using  '$('#UT, #LT').mapster(default_options)' we must use this.$el.find('#UT,#LT').mapster(default_options)
//})///////////////////CHARTATION??????????with working svg
odoo.define('pragtech_dental_management.chart_action', function(require) {
	"use strict";

	var core = require('web.core');
	var WebClient = require('web.WebClient');
	var Widget = require('web.Widget');
//	var Models = require('web.Model');
//	var Model = require('web.DataModel');
	var rpc = require('web.rpc');
	var session = require('web.session');
	var _t = core._t;
	var _lt = core._lt;
	var QWeb = core.qweb;
	var Class = core.Class;

	//Dental Chart variables
	var operation_id = 0;
	var full_mouth_selected = 0;
	var upper_mouth_selected = 0;
	var lower_mouth_selected = 0;
	var selected_treatment = '';
	var selected_tooth = '';
	var tooth_by_part = 0;
	var tid = '';
	var toothmap_id = '';
	var toothmap_list = new Array();
	var keyList = new Array();
	var imageMapList = new Array();
	var selected_surface = new Array();

	console.log("Loaddddddd   ")
	console.log("Selected surface   ",selected_surface)
	var is_tooth_select = false
	var selected_category = '';
	var treatment_lines = new Array();
	var full_mouth_teeth = new Array();
	var Missing_Tooth = 0;
	var NO_OF_TEETH = 32;
	var teethcount = 0;
	var user_name = '';
	var cont = true;
	var update = false;
	var action_on_teeth = new Array();
	var other_patient_history = new Array();
	var self_var;
	//Tooth Number selection array list
	var Palmer;
	// create an empty array
	var Iso;
	//Chart Selection Check
	var type = '';

	//Chart Selection Check
	var type = '';

	var DentalChartView = Widget.extend({
		template : "DentalChartView",

		init : function(parent, options) {
			this._super(parent);
			var self = this;
			operation_id = 0;
			selected_treatment = '';
			selected_tooth = '';
			full_mouth_selected = 0;
			toothmap_id = '';
			tooth_by_part = 0;
		//	selected_surface.length = 0;
			selected_category = '';
			treatment_lines.length = 0;
			Missing_Tooth = 0;
			other_patient_history = new Array();
			NO_OF_TEETH = 32;
			user_name = '';
			cont = true;
			update = false;
            var checkVal = '';
			self.patient_id = options.params.patient_id;
			self.appointment_id = options.params.appt_id;
			self.get_user(session.partner_id);
            self.type = options.params.type;
			type = self.type;
			//chart selection variable



			if (type == 'palmer') {
				var palmer = {
					'1' : '8-1x',
					'2' : '7-1x',
					'3' : '6-1x',
					'4' : '5-1x',
					'5' : '4-1x',
					'6' : '3-1x',
					'7' : '2-1x',
					'8' : '1-1x',
					'9' : '1-2x',
					'10' : '2-2x',
					'11' : '3-2x',
					'12' : '4-2x',
					'13' : '5-2x',
					'14' : '6-2x',
					'15' : '7-2x',
					'16' : '8-2x',
					'17' : '8-3x',
					'18' : '7-3x',
					'19' : '6-3x',
					'20' : '5-3x',
					'21' : '4-3x',
					'22' : '3-3x',
					'23' : '2-3x',
					'24' : '1-3x',
					'25' : '1-4x',
					'26' : '2-4x',
					'27' : '3-4x',
					'28' : '4-4x',
					'29' : '5-4x',
					'30' : '6-4x',
					'31' : '7-4x',
					'32' : '8-4x',

				};
				Palmer = palmer;
			}

			if (type == 'iso') {
				var iso = {
					'1' : '18',
					'2' : '17',
					'3' : '16',
					'4' : '15',
					'5' : '14',
					'6' : '13',
					'7' : '12',
					'8' : '11',
					'9' : '21',
					'10' : '22',
					'11' : '23',
					'12' : '24',
					'13' : '25',
					'14' : '26',
					'15' : '27',
					'16' : '28',
					'17' : '38',
					'18' : '37',
					'19' : '36',
					'20' : '35',
					'21' : '34',
					'22' : '33',
					'23' : '32',
					'24' : '31',
					'25' : '41',
					'26' : '42',
					'27' : '43',
					'28' : '44',
					'29' : '45',
					'30' : '46',
					'31' : '47',
					'32' : '48',
				};
				Iso = iso;
			}

			self.patient_history().then(function(res) {
				self.write_patient_history(self, other_patient_history);


				 $("div.childteethchart").hide();
                 $("div.teethchartadult").hide();
                 $("div.mapdetails").hide();
                 _.each(other_patient_history, function(each_operation) {
				  console.log("touched line 463")

                    imageMapList = each_operation['surface'];
                    var ts = imageMapList ;
                    var tooth_surface = ts.slice(0,-3);
                    var tempImageMapList = new Array();
                    //var tooth_surface = (imageMapList[0].split('_'))[0];

					console.log('inside fn call line 458 ts is',imageMapList,ts,tooth_surface);

                      var surface_chk =((tooth_surface == 'root')||(tooth_surface == 'crown')||(tooth_surface == 'toothcap'));
                      console.log("checking the surface ",surface_chk);


                        if ((each_operation.tooth_id) && (!surface_chk)){

                            console.log("before calling colouring function.......")
                            self.color_surfaces(svg, each_operation['surface'].split(' '), each_operation['tooth_id'], self);

                        }
                        else if((each_operation.tooth_id) && (surface_chk)) {

                         tempImageMapList.push(imageMapList);
				          var mapkeystr = tempImageMapList +',';

                         console.log("putting toothkeys and calling mapster directly",mapkeystr);
                        // localStorage.setItem('test', mapkeystr);
                        self.$el.find.greet;



                         return;

                            }
                        else
                        {
                          if(each_operation['surface'] == 'Full_mouth'){
                          self.add_selection_action(each_operation['multiple_teeth']);
                          }
                          if((each_operation['surface']=='Upper_Jaw')||(each_operation['surface']=='Lower_Jaw')){
                             var keystr = '';
                             if(each_operation['surface']=='Upper_Jaw'){
                             for ( var i=1; i<=17;i++)
                                       keystr += ',tooth_'+i;
                                      console.log('in on load from history',keystr);
                                     localStorage.setItem('upperkeys', keystr);
                              }
                             if(each_operation['surface']=='Lower_Jaw'){
                             for ( var i=16; i<=33;i++)
                                       keystr += ',tooth_'+i;
                                      console.log('in chart action',keystr);
                                     localStorage.setItem('lowerkeys', keystr);
                              }

                          }
                          each_operation.tooth_id = '-';
                            if (each_operation['desc']['action'] == 'missing') {
                                self.perform_missing_action(each_operation['multiple_teeth']);
                                }
                        }

				});
   self.$('.chartselect').click(function() {
	//$("input[name$='chartoption']").change(function() {
   var checkVal = $(this).val();
         alert(checkVal);

         if(checkVal == "adult") {
         $("div.childteethchart").hide();
         $("div.teethchartadult").show();
         displaySVGBox(checkVal);
         }
         if(checkVal == "child"){
           $("div.teethchartadult").hide();
           $("div.childteethchart").show();
          displaySVGBox(checkVal);

         }
$('#teethchart_child').removeClass('hidden');
$('#svg_child').removeClass('hidden');
$('#child_lowermouth').removeClass('hidden');

var svg1 = $('#svgchild1')[0];
var svg2 = $('#svg_object_child')[0];
var svg3 = $('#svgchild2')[0];

                	$(".view").click(function() {
                	var _this = $(this);
					console.log('in click-------------')
					console.log("tooth_by_part",tooth_by_part)
					if (!cont || update) {
						selected_surface.length = 0;
						cont = true;
					} else {
						console.log("Else In click ----")
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
					var found_selected_operation = self.$el.find('.selected_operation');
					if (found_selected_operation[0]) {
						console.log("FOund selected operation")
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
					if (1) {
                        console.log("KKKKKKKKKKKK")
                        console.log("inside click view fn",selected_tooth)


						if ($("#" + _this.attr('id')).attr('fill') == 'white') {
							console.log("11111111111111   ",is_tooth_select)

							$("#" + _this.attr('id')).attr('fill', 'orange');
							console.log("==============    ",selected_surface)
							var available = selected_surface.indexOf(this.id);
							console.log("Available  -->>>> ",available)
							if(available == -1 && is_tooth_select == false){
								console.log("pppppppuuuuuushh 1")

								selected_surface.push(this.id);
							}

						} else if (parseInt(($("#" + _this.attr('id')).attr('class')).split(' ')[3]) == 0){
							console.log("222222222222222")
							is_tooth_select = false
							$("#" + _this.attr('id')).attr('fill', 'white');
							var index = selected_surface.indexOf(this.id);
							selected_surface.splice(index, 1);
						} else {
							console.log("3333333333333333333  ",$("#" + _this.attr('id')))
							console.log("-------**-    ",$("#" + _this.attr('id')).attr('fill'))
//
							if ($("#" + _this.attr('id')).attr('fill') == 'orange') {
							$("#" + _this.attr('id')).attr('fill', 'white');
							console.log("Thisssssssssssssssssssss   *   ",this.id)
							is_tooth_select = true
							console.log("  &&&&&&&&     ",selected_surface)
							var current_tooth_id = this.id.lastIndexOf("_")
							var res = this.id.slice(current_tooth_id, this.id.length);
							console.log("RESSSSSSSSSSSSSSSSSSS   ",res)

							}
							else{
								console.log("44444444444444444444");
								selected_surface.push(this.id);

							}
						}
					}
//					console.log('selected_surface',selected_surface,selected_surface.length)
				});





		});

				$("img").click(function() {
					if (!selected_treatment) {
						if ($(this).attr('class') == 'selected_tooth') {
							$(this).removeClass('selected_tooth');
							self.decrement_thread(['view_' + this.id + '_bottom', 'view_' + this.id + '_center', 'view_' + this.id + '_right', 'view_' + this.id + '_left', 'view_' + this.id + '_top']);
							if (document.getElementById('view_' + this.id + '_center').classList[3] == "0")
								$('#view_' + this.id + '_center').attr('fill', 'white');
							if (document.getElementById('view_' + this.id + '_right').classList[3] == "0")
								$('#view_' + this.id + '_right').attr('fill', 'white');
							if (document.getElementById('view_' + this.id + '_left').classList[3] == "0")
								$('#view_' + this.id + '_left').attr('fill', 'white');
							$('#view_' + this.id + '_top').attr('fill', 'white');
							$('#view_' + this.id + '_bottom').attr('fill', 'white');
							selected_surface.length = 0;
						} else {
							$(this).attr('class', 'selected_tooth');
							$('#view_' + this.id + '_center').attr('fill', 'orange');
							$('#view_' + this.id + '_right').attr('fill', 'orange');
							$('#view_' + this.id + '_left').attr('fill', 'orange');
							$('#view_' + this.id + '_top').attr('fill', 'orange');
							$('#view_' + this.id + '_bottom').attr('fill', 'orange');
							self.increment_thread(['view_' + this.id + '_bottom', 'view_' + this.id + '_center', 'view_' + this.id + '_right', 'view_' + this.id + '_left', 'view_' + this.id + '_top']);
						}
						return;
					}
					selected_tooth = this.id;
					console.log("Execute Create 111");
					self.execute_create(false, self, false);

					switch(selected_treatment.action) {
					case 'missing':
						if ($("#" + $(this).attr('id')).attr('class') == "teeth") {
							// $($("#" + $(this).attr('id')).attr('src', "/pragtech_dental_management/static/src/img/images.png").attr('class', 'blank'));
							$($("#" + $(this).attr('id')).attr('class', 'blank'));
							$($("#" + $(this).attr('id'))).css('visibility', 'hidden');
							$("#view_" + $(this).attr('id') + "_top,#view_" + $(this).attr('id') + "_left,#view_" + $(this).attr('id') + "_bottom,#view_" + $(this).attr('id') + "_right,#view_" + $(this).attr('id') + "_center").attr('visibility', 'hidden');
						} else {
							$($("#" + $(this).attr('id')).css('visibility', 'visible').attr('class', 'teeth'));
							$("#view_" + $(this).attr('id') + "_top,#view_" + $(this).attr('id') + "_left,#view_" + $(this).attr('id') + "_bottom,#view_" + $(this).attr('id') + "_right,#view_" + $(this).attr('id') + "_center").attr('visibility', 'visible');
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

		 var map1 = document.getElementById("toothmapupper");
		 var map2 = document.getElementById("toothmaplower");
         map1.addEventListener("click", toothmapFunction);
         map2.addEventListener("click", toothmapFunction);
		//we attach an event listener to the parent
         function toothmapFunction(e){


		   var keyList= 'none';
			//e.currentTarget : to which event listener is attached
			//e.target: the element which was clicked
			if(e.target !== e.currentTarget){
			   //we only need to hear events from the area (children of map), so we ignore any other events that are called when the parent is clicked by this if statement
				tid = e.target.id;
				console.log("here is map area id" ,tid)
				var t = new Array();
				t = tid.split('_');
				toothmap_id = t[1];
				console.log("tooth map id extract"+ toothmap_id);
				selected_tooth = toothmap_id;
                tooth_by_part = 1;



			}
			e.stopPropagation(); //we stop the propagation of event to the DOM once its purpose is solved
			}

				$(".view").click(function() {
					console.log('in click-------------')
					console.log("tooth_by_part",tooth_by_part)
					if (!cont || update) {
						selected_surface.length = 0;
						cont = true;
					} else {
						console.log("Else In click ----")
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
					var found_selected_operation = self.$el.find('.selected_operation');
					if (found_selected_operation[0]) {
						console.log("FOund selected operation")
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
					if (1) {
                        console.log("KKKKKKKKKKKK")
                        console.log("inside click view fn",selected_tooth)
                             //if ($("#" + $(this).attr('id')).attr('fill') == 'white') {
//							//selected_surface.push(this.id);//js
//							$("#" + $(this).attr('id')).attr('fill', 'orange');
//						}
//						else if (parseInt(($("#" + $(this).attr('id')).attr('class')).split(' ')[3]) == 0) {
//
//							if($("#" + $(this).attr('id')).attr('fill')=='orange')//js
//							{
//							$("#" + $(this).attr('id')).attr('fill', 'white');
//							}
//							var index = selected_surface.indexOf(this.id);
//							selected_surface.splice(index, 1);
//						}
//						else {
//							selected_surface.push(this.id);
//							$("#" + $(this).attr('id')).attr('fill', 'white');//js
//						}
						if ($("#" + $(this).attr('id')).attr('fill') == 'white') {
							console.log("11111111111111   ",is_tooth_select)
							$("#" + $(this).attr('id')).attr('fill', 'orange');
							console.log("==============    ",selected_surface)
							var available = selected_surface.indexOf(this.id);
							console.log("Available  -->>>> ",available)
							if(available == -1 && is_tooth_select == false){
								console.log("pppppppuuuuuushh 1")

								selected_surface.push(this.id);
							}

						} else if (parseInt(($("#" + $(this).attr('id')).attr('class')).split(' ')[3]) == 0){
							console.log("222222222222222")
							is_tooth_select = false
							$("#" + $(this).attr('id')).attr('fill', 'white');
							var index = selected_surface.indexOf(this.id);
							selected_surface.splice(index, 1);
						} else {
							console.log("3333333333333333333  ",$("#" + $(this).attr('id')))
							console.log("-------**-    ",$("#" + $(this).attr('id')).attr('fill'))
//
							if ($("#" + $(this).attr('id')).attr('fill') == 'orange') {
							$("#" + $(this).attr('id')).attr('fill', 'white');
							console.log("Thisssssssssssssssssssss   *   ",this.id)
							is_tooth_select = true
							console.log("  &&&&&&&&     ",selected_surface)
							var current_tooth_id = this.id.lastIndexOf("_")
							var res = this.id.slice(current_tooth_id, this.id.length);
							console.log("RESSSSSSSSSSSSSSSSSSS   ",res)

							}
							else{
								console.log("44444444444444444444");
								selected_surface.push(this.id);

							}
						}
					}
//					console.log('selected_surface',selected_surface,selected_surface.length)
				});

				self.get_treatment_cats().then(function(res) {
					var treatment_list = res;
					var total_list_div = '';
					for (var j = 0; j < treatment_list.length; j++) {
						total_list_div += '<div class="panel-heading"><h4 class="panel-title"><a id="categ_' + treatment_list[j].treatment_categ_id + '"data-toggle="collapse" href="#collapse' + treatment_list[j].treatment_categ_id + '">' + treatment_list[j].name + '</a></h4></div>';
						total_list_div += '<div id="collapse' + treatment_list[j].treatment_categ_id + '" class="panel-collapse collapse"><div class="panel-body">';
						_.each(treatment_list[j].treatments, function(each_one) {
							if (each_one.action == 'missing') {
								missing = each_one.treatment_id;
							}
							total_list_div += '<li id = "treat_' + treatment_list[j].treatment_categ_id + '_' + each_one['treatment_id'] + '">' + each_one['treatment_name'] + '</li>';

						});
						total_list_div += '</div></div>';
					}
					$('#total_list_div').append(total_list_div);
					self.categ_list = treatment_list;
					for (var i = 0; i < self.categ_list.length; i++) {
						$('#categ_' + self.categ_list[i].treatment_categ_id).click(function() {
							if (selected_surface) {
								var found_selected_categ = self.$el.find('.selected_category');
								if (found_selected_categ) {
									found_selected_categ.removeClass("selected_category");
								}
								selected_treatment = '';
								$('#' + this.id).attr('class', 'selected_category');
								var categ_no = parseInt(this.id.substr(6));
								self.$('#treatments_list').empty();
								for (var k = 0; k < self.categ_list.length; k++) {
									if (self.categ_list[k].treatment_categ_id == categ_no) {
										_.each(self.categ_list[k].treatments, function(each_treatment) {
											$('#treat_' + categ_no + '_' + each_treatment.treatment_id).attr('data-selected', 'false');
											$('#treat_' + categ_no + '_' + each_treatment.treatment_id).click(function() {
											    var found_selected_tooth;
												if (full_mouth_selected == 1) {
                                                  console.log('inside fullmouthcall');
													self.put_data_full_mouth(self, full_mouth_teeth, full_mouth_selected, each_treatment, 'planned','Full_mouth',false, false, false);
													full_mouth_selected = 0;
													return;
												}
												if (upper_mouth_selected == 1) {
                                                    var upper_mouth = new Array();
                                                    for (var select_up_tooth = 1; select_up_tooth <= 16; select_up_tooth++) {
                                                    upper_mouth.push(select_up_tooth);}
												    console.log('inside uppermouthcall');
													self.put_data_full_mouth(self, upper_mouth, upper_mouth_selected, each_treatment, 'planned', 'Upper_Jaw',false, false, false);
													upper_mouth_selected = 0;
													return;
												}
												if (lower_mouth_selected == 1) {
												    var lower_mouth = new Array();
                                                    for (var select_up_tooth = 1; select_up_tooth <= 16; select_up_tooth++) {
                                                    lower_mouth.push(select_up_tooth);}
												    console.log('inside lower_mouthcall');
													self.put_data_full_mouth(self, lower_mouth, lower_mouth_selected, each_treatment, 'planned','Lower_Jaw',false, false, false);
													lower_mouth_selected = 0;
													return;
												}

                                                if (tooth_by_part == 1) {

												found_selected_tooth = toothmap_id;
												selected_surface = tid;

                                                self.put_data_toothpart(self_var, found_selected_tooth, selected_surface, tooth_by_part, each_treatment,'planned', false, false, false) ;

//												if (found_selected_tooth[0]) {
//													selected_surface.length = 0;
//												}
//												console.log("found_selected_tooth  [toothmapid] ",found_selected_tooth[0])
//												console.log("selected_surface ---[tid]   ",selected_surface)
//
//												if(each_treatment.action != 'missing'){
//														var found = self.$el.find('.selected_treatment');
//														if (found) {
//															found.removeClass("selected_treatment");
//														}
//														$('#treat_' + categ_no + '_' + each_treatment.treatment_id).attr('class', 'selected_treatment');
//														selected_treatment = each_treatment;
//														console.log("Execute Create 22222222222 toooooooooooooth  ",selected_surface);
//														self.execute_create(false, self, selected_surface);
//													}

                                                    tooth_by_part == 0;

                                                return;
												}

												cont = false;



												var found_selected_tooth = self.$el.find('.selected_tooth');
												if (found_selected_tooth[0]) {
													selected_surface.length = 0;
												}
												console.log("found_selected_tooth   ",found_selected_tooth[0])
												console.log("selected_surface ---   ",selected_surface)
												is_tooth_select = false

												if (selected_surface[0]) {
													if(each_treatment.action != 'missing'){
														var found = self.$el.find('.selected_treatment');
														if (found) {
															found.removeClass("selected_treatment");
														}
														$('#treat_' + categ_no + '_' + each_treatment.treatment_id).attr('class', 'selected_treatment');
														selected_treatment = each_treatment;
														console.log("Execute Create 22222222222  ",selected_surface);
														self.execute_create(true, self, selected_surface);
													}
													else{
														var answer = confirm('Complete tooth has to be missing, not the selected surfaces.\nClick OK to remove the complete tooth')
														if(answer){
															var tooth_id = selected_surface[0].split('_')[1]
															$('#'+tooth_id).attr('class','selected_tooth')
															found_selected_tooth = self.$el.find('.selected_tooth');
														}
													}
												}

												if (found_selected_tooth[0]) {
													if (!found_selected_tooth[0])
														alert('** 727**Please select the surface first !');
													else {
														var found = self.$el.find('.selected_treatment');
														if (found) {
															found.removeClass("selected_treatment");
														}
														$('#treat_' + categ_no + '_' + each_treatment.treatment_id).attr('class', 'selected_treatment');
                                                        selected_treatment = each_treatment;
														_.each(found_selected_tooth, function(each_found_selected_tooth) {
															selected_tooth = each_found_selected_tooth.id;
															console.log("*************    ",selected_tooth)
															selected_surface.length = 0;
															if($("#" +'view_' + selected_tooth + '_top').attr('fill') == 'orange'){
																selected_surface.push('view_' + selected_tooth + '_top');
															}
															if($("#" +'view_' + selected_tooth + '_bottom').attr('fill') == 'orange'){
																selected_surface.push('view_' + selected_tooth + '_bottom');
															}
															if($("#" +'view_' + selected_tooth + '_center').attr('fill') == 'orange'){
																selected_surface.push('view_' + selected_tooth + '_center');
															}
															if($("#" +'view_' + selected_tooth + '_right').attr('fill') == 'orange'){
																selected_surface.push('view_' + selected_tooth + '_right');
															}
															if($("#" +'view_' + selected_tooth + '_left').attr('fill') == 'orange'){
																selected_surface.push('view_' + selected_tooth + '_left');
															}
															console.log("##########################    ", $("#" +'view_' + selected_tooth + '_top').attr('fill') )




															if (each_treatment.action == 'missing') {
																Missing_Tooth.push(parseInt(selected_tooth));
																self.perform_missing_action([selected_tooth]);
															}
															console.log("Execute Create 33333335 " );
															console.log("Surfaceeeeeeeeeeeee  &&&&&&&&&&&& ",selected_surface)
															self.execute_create(true, self, false);
															$(each_found_selected_tooth).removeClass('selected_tooth');
														});
														selected_surface.length = 0;
													}
												}
												if (!found_selected_tooth[0] && !selected_surface[0]) {
													alert('**772***Please select the surface first !');
													return;
												}
												$('#' + this.id).removeClass('selected_treatment');
												selected_treatment = '';
											});
										});
										break;
									}
								}
							} else {
								alert('Select a tooth first!!');
							}
						});
					}

				});

			});
		},

		perform_missing_action : function(missing_tooth_ids) {
			_.each(missing_tooth_ids, function(each_of_missing_tooth_ids) {
				// $('#' + String(each_of_missing_tooth_ids)).attr('src', "/pragtech_dental_management/static/src/img/images.png");
				$('#' + String(each_of_missing_tooth_ids)).css('visibility', 'hidden').attr('class', 'blank');
				$('#view_' + String(each_of_missing_tooth_ids) + '_top').attr('visibility', 'hidden');
				$('#view_' + String(each_of_missing_tooth_ids) + '_bottom').attr('visibility', 'hidden');
				$('#view_' + String(each_of_missing_tooth_ids) + '_left').attr('visibility', 'hidden');
				$('#view_' + String(each_of_missing_tooth_ids) + '_right').attr('visibility', 'hidden');
				$('#view_' + String(each_of_missing_tooth_ids) + '_center').attr('visibility', 'hidden');
			});
		},

		remove_missing_action : function(missing_tooth_ids) {
			_.each(missing_tooth_ids, function(each_of_missing_tooth_ids) {
				$('#' + String(each_of_missing_tooth_ids)).css('visibility', 'visible').attr('class', 'teeth');
				;
				$('#view_' + String(each_of_missing_tooth_ids) + '_top').attr('visibility', 'visible');
				$('#view_' + String(each_of_missing_tooth_ids) + '_bottom').attr('visibility', 'visible');
				$('#view_' + String(each_of_missing_tooth_ids) + '_left').attr('visibility', 'visible');
				$('#view_' + String(each_of_missing_tooth_ids) + '_right').attr('visibility', 'visible');
				$('#view_' + String(each_of_missing_tooth_ids) + '_center').attr('visibility', 'visible');
			});
		},

		remove_selection_action : function(nonselection_ids) {
			_.each(nonselection_ids, function(each_of_nonselection_ids) {
				if (document.getElementById('view_'+String(each_of_nonselection_ids)+"_top").classList[3] == '0')
					$('#view_' + String(each_of_nonselection_ids) + '_top').attr('fill', 'white');
				if (document.getElementById('view_'+String(each_of_nonselection_ids)+"_bottom").classList[3] == '0')
					$('#view_' + String(each_of_nonselection_ids) + '_bottom').attr('fill', 'white');
				if (document.getElementById('view_'+String(each_of_nonselection_ids)+"_left").classList[3] == '0')
					$('#view_' + String(each_of_nonselection_ids) + '_left').attr('fill', 'white');
				if (document.getElementById('view_'+String(each_of_nonselection_ids)+"_right").classList[3] == '0')
					$('#view_' + String(each_of_nonselection_ids) + '_right').attr('fill', 'white');
				if (document.getElementById('view_'+String(each_of_nonselection_ids)+"_center").classList[3] == '0')
					$('#view_' + String(each_of_nonselection_ids) + '_center').attr('fill', 'white');
			});
		},
		add_selection_action : function(selection_ids) {
			_.each(selection_ids, function(each_of_selection_ids) {
				$('#view_' + String(each_of_selection_ids) + '_top').attr('fill', 'orange');
				$('#view_' + String(each_of_selection_ids) + '_bottom').attr('fill', 'orange');
				$('#view_' + String(each_of_selection_ids) + '_left').attr('fill', 'orange');
				$('#view_' + String(each_of_selection_ids) + '_right').attr('fill', 'orange');
				$('#view_' + String(each_of_selection_ids) + '_center').attr('fill', 'orange');
			});
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

					console.log("Prgogresss  writing patient history ")

					imageMapList = each_operation['surface'];
                    var ts = imageMapList ;
                    var tooth_surface = ts.slice(0,-3);
                    var surface_chk =((tooth_surface == 'root')||(tooth_surface == 'crown')||(tooth_surface == 'toothcap'));
					console.log('write while  writing patient history',tooth_surface,imageMapList,surface_chk);

					if((tooth_surface == 'root')||(tooth_surface == 'crown')||(tooth_surface == 'toothcap'))
					{

                     var mapkeys = $('#showkeylist').val();

                     $('#showkeylist').val(imageMapList+','+mapkeys);
                     keyList.push(imageMapList);
				     var mapkeystr = keyList +',';

                    console.log("reachedhere to put toothkeys",mapkeystr);
                    localStorage.setItem('test', mapkeystr);

                    }

					self_var.put_data(self_var, each_operation['surface'].split(' '), each_operation['tooth_id'], false, each_operation['status'], each_operation['created_date'], is_prev_record_from_write, each_operation['other_history']);
				}
				else {
				console.log("reached line 1048........before putting in page")
					self_var.put_data_full_mouth(self_var, each_operation.multiple_teeth, 1, selected_treatment, each_operation['status'],each_operation['surface'], each_operation['created_date'], is_prev_record_from_write, each_operation['other_history']);

				}
			});
			selected_treatment = '';
		},

		renderElement : function(parent, options) {
			this._super(parent);
			var self = this;

            self.$('#select_full_mouth').change(function() {
        		if (this.checked) {
					full_mouth_selected = 1;
				} else {
					full_mouth_selected = 0;
				}
             	var miss = 0;
				var full_mouth = new Array();
				for (var select_all_tooth = 1; select_all_tooth <= 32; select_all_tooth++) {
					miss = 0;
					for (var each_from_missing = 0; each_from_missing < Missing_Tooth.length; each_from_missing++) {
						if (Missing_Tooth[each_from_missing] == parseInt(select_all_tooth)) {
							miss = 1;
							break;
						}
					}
					if (!miss && full_mouth_selected) {
						full_mouth.push(select_all_tooth);
						self.$('#view_' + select_all_tooth + "_center").attr('fill', 'orange');
						self.$('#view_' + select_all_tooth + "_top").attr('fill', 'orange');
						self.$('#view_' + select_all_tooth + "_right").attr('fill', 'orange');
						self.$('#view_' + select_all_tooth + "_left").attr('fill', 'orange');
						self.$('#view_' + select_all_tooth + "_bottom").attr('fill', 'orange');
					} else if (!miss) {
						full_mouth.push(select_all_tooth);
						if (document.getElementById('view_'+select_all_tooth+"_center").classList[3] == 0)
							self.$('#view_' + select_all_tooth + "_center").attr('fill', 'white');
						if (document.getElementById('view_'+select_all_tooth+"_top").classList[3] == 0)
							self.$('#view_' + select_all_tooth + "_top").attr('fill', 'white');
						if (document.getElementById('view_'+select_all_tooth+"_bottom").classList[3] == 0)
							self.$('#view_' + select_all_tooth + "_bottom").attr('fill', 'white');
						if (document.getElementById('view_' + select_all_tooth + "_right").classList[3] == 0)
							self.$('#view_' + select_all_tooth + "_right").attr('fill', 'white');
						if (document.getElementById('view_'+select_all_tooth+"_left").classList[3] == 0)
							self.$('#view_' + select_all_tooth + "_left").attr('fill', 'white');
					}
				}
				full_mouth_teeth = full_mouth;

			});
//			self.$('.myButton').click(function() {
//				var current_obj = this;
//				var found = self.$el.find('.progress_table_actions');
//				_.each(found, function(each_found) {
//					if (each_found.innerText != 'missing') {
//						var actual_id = each_found.id.substr(7);
//						if ($('#status_'+actual_id)[0].innerHTML != 'Completed') {
//							$('#status_'+actual_id)[0].innerHTML = (current_obj.innerHTML).trim();
//						}
//					}
//				});
//			});


                self.$('.jaw').click(function()
                {
                 $('input:checkbox[name=mouthselection]').each(function()
                                {

                                    if($(this).is(':checked'))
                                    {
                                      console.log($(this).val());
                                      var selected_chkbox =($(this).val());
                                      var keystr = 'tooth';
                                      if (selected_chkbox == 'uppermouth'){
                                      for ( var i=1; i<=17;i++)
                                       keystr += ',tooth_'+i;
                                      console.log('in chart action',keystr);
                                     localStorage.setItem('upperkeys', keystr);
                                     upper_mouth_selected = 1;

                                      };
                                      if (selected_chkbox == 'lowermouth'){
                                      for ( var i=16; i<=33;i++)
                                       keystr += ',tooth_'+i;
                                      console.log('in chart action',keystr);
                                     localStorage.setItem('lowerkeys', keystr);
                                     lower_mouth_selected = 1;
                                      };
                                    }
                                });
                });


                self.$('.myButton').click(function() {
				var current_obj = this;
				var found = $('.selected_operation').find('.progress_table_actions');
				_.each(found, function(each_found) {
					if (each_found.innerText != 'missing') {
						var actual_id = each_found.id.substr(7);

						if ($('#status_'+actual_id).attr('status_name') != 'completed') {
							$('#status_'+actual_id).attr('status_name', current_obj.id)
							$('#status_'+actual_id)[0].innerHTML = (current_obj.innerHTML).trim();

						}
						else if($('#status_'+actual_id).attr('status_name') == 'completed') {
							$('#status_'+actual_id)[0].innerHTML = $('#completed').text().trim();
						}
					}
				});
				if (!found.length) {
					alert('Please select a record!')
				}

			});

			self.$('#heading').click(function() {
				var found = self.$el.find('.selected_operation');
				if (found) {
					found.removeClass("selected_operation");
				}
			});

//			self.$('#refresh_screen').click(function(){
//			window.location.reload();
//			self.perform_action().then(function() {
//				console.log('i m at line 1149 self.perform_action and .then')
//
//
//				});
//			});
			self.$('#close_screen').click(function() {
			   // localStorage.clear();
				console.log("Perform Action  click on close button::::::   ")
				self.perform_action().then(function() {
				self.window_close();
             });
			});

			rpc.query({
                model: 'teeth.code',
                method: 'get_teeth_code',
                args: [this.patient_id],
            })
            .then(function(res){

//			new Model('teeth.code').call('get_teeth_code', [this.patient_id]).then(function(res) {

				var name = "";
				var j = 0;
				var k = 7;
				var l = 0;

				if (type == 'universal') {
					for (var i = 0; i < 16; i++) {
						name = "<td  width = '46px' id='teeth_" + i + "'>" + res[i] + "</td>";
						$('#upper_teeths').append(name);
					}
					for (var i = 31; i > 15; i--) {
						name = "<td  width = '46px' id='teeth_" + i + "'>" + res[i] + "</td>";
						$('#lower_teeths').append(name);

					}
				} else if (type == 'palmer') {
					for (var i = 7; i >= 0; i--) {
						name = "<td  width = '47px' id='teeth_" + i + "'>" + res[i] + "</td>";
						$('#upper_teeths').append(name);

					}
					for (var i = 7; i < 15; i++) {

						name = "<td  width = '47px' id='teeth_" + i + "'>" + res[j] + "</td>";
						$('#upper_teeths').append(name);
						j++;

					}
					for (var i = 23; i > 15; i--) {

						name = "<td  width = '47px' id='teeth_" + i + "'>" + res[k] + "</td>";
						$('#lower_teeths').append(name);
						k--;
					}
					for (var i = 24; i < 32; i++) {
						name = "<td  width = '47px' id='teeth_" + i + "'>" + res[l] + "</td>";
						$('#lower_teeths').append(name);
						l++;
					}

				} else if (type == 'iso') {
					for (var i = 0; i <= 7; i++) {

						name = "<td  width = '46px' id='teeth_" + i + "'>" + res[i] + "</td>";
						$('#upper_teeths').append(name);

					}
					for (var i = 8; i <= 15; i++) {

						name = "<td  width = '46px' id='teeth_" + i + "'>" + res[i] + "</td>";
						$('#upper_teeths').append(name);

					}
					for (var i = 31; i >= 24; i--) {

						name = "<td  width = '46px' id='teeth_" + i + "'>" + res[i] + "</td>";
						$('#lower_teeths').append(name);

					}
					for (var i = 23; i >= 16; i--) {
						name = "<td  width = '46px' id='teeth_" + i + "'>" + res[i] + "</td>";
						$('#lower_teeths').append(name);

					}

				}
			});


},
		perform_action : function() {
			var $def = $.Deferred();
			var p_id;
			var treatment_lines_2 = new Array();
			{
				console.log("Lineeeeeeeeeee 11111111111111")
				for (var op = 1; op <= operation_id; op++) {
					var op_id = document.getElementById('operation_' + op);
					// $('#operation_' + op).css('display')
					if (op_id) {
						$('#operation_' + op).removeClass('selected_operation');
						var teeth_id = document.getElementById('tooth_' + op);
						console.log("teeth_id",teeth_id);
                        var created_date = document.getElementById('date_time_' + op);
						var prev_record = document.getElementById('previous_' + op);
						var status_id = document.getElementById('status_' + op);
						var status_name = $(status_id).attr('status_name');
						var dentist = document.getElementById('dentist_' + op);
						var surface = document.getElementById('surface_' + op);
						var desc = document.getElementById('desc_' + op);
						var categ_id = $(desc).attr('class');
						var surface_list = String(surface.innerHTML).split(' ');
						var tooth = $('#tooth_' + op).attr('class');
                        var all_teeth = op_id.className;
						var values = [];
						var vals = [];
						_.each(surface_list, function(each_surface) {
							vals.push(each_surface);
						});
						var categ_list = new Array();
						categ_list.push({
							'categ_id' : categ_id,
							'values' : vals
						});
						values.push(categ_list);
						var actual_tooth = String(teeth_id.id);
						console.log("inside perform action " ,"teeth_id  document.getElementById('tooth_' + op)"+teeth_id,"tooth $('#tooth_' + op).attr('class');"+tooth,"actual_tooth = String(teeth_id.id);"+actual_tooth);
						treatment_lines_2.push({
							'status' : String(status_id.innerHTML),
							'status_name' : status_name,
							'teeth_id' : tooth,
							'dentist' : session.uid,
							'values' : categ_list,
							'prev_record' : prev_record.innerHTML,
							'multiple_teeth' : all_teeth,
						});

						console.log("Treatment lines printing ---------------")
						console.log(treatment_lines_2);

					}
				}
			}

			rpc.query({
                model: 'medical.patient',
                method: 'create_lines',
                args: [this.patient_id, treatment_lines_2, this.patient_id, this.appointment_id],
            })
            .then(function(res) {
               treatment_lines_2 = new Array();
               $def.resolve(res);
            });
//			new Model('medical.patient').call('create_lines', [this.patient_id, treatment_lines_2, this.patient_id, this.appointment_id]).then(function(res) {
//				treatment_lines_2 = new Array();
//				$def.resolve(res);
//			});
			return $def;
        console.log('i m at line 1294');

		},
		window_close : function() {
		    localStorage.removeItem('test');
			localStorage.removeItem('upperkeys');
			localStorage.removeItem('lowerkeys');
			console.log(".........i am at line 1300.....")
			//this.trigger_up('history_back');
			this.do_action({
				type : 'ir.actions.client',
				tag : 'history_back'
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
			console.log(" inside execute create ---Selected surface temp, selected tooth -- ",selected_surface_temp,selected_tooth)
			if (!selected_surface_temp) {
				selected_surface_temp = selected_surface;
			}


			var tooth_present = 0;

			//if(!tooth_by_part){

			 tooth_present = this.check_if_tooth_present(selected_tooth);
			//}


			var record = new Array();
			record['treatments'] = new Array();
			record['tooth_id'] = selected_tooth;
			var surfaces = new Array();
			_.each(selected_surface_temp, function(each_surface) {
				var surface = ($('#'+each_surface).attr('class')).split(' ')[1];
				console.log("Each Surface **  ",surface)
				surfaces.push(surface);
			});
			var d = new Array();
			d = {
				'treatment_id' : selected_treatment['treatment_id'],
				'vals' : surfaces
			};
			console.log(" ddddddddddd   ",d)
			var selected_tooth_temp = selected_tooth;
			if (attrs) {
				if (!tooth_present) {
					record['treatments'].push(d);
					treatment_lines.push(record);
					console.log("Outtt 222222  ",surfaces)
					this.put_data(self_var, surfaces, selected_tooth_temp, selected_surface_temp, 'planned', false, false, false);
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
								console.log("Putttt  333333 *******************")
								this.put_data(self_var, surfaces, selected_tooth_temp, selected_surface_temp, false, false, false, false);
							}
						}
					}

				}
			} else {
				if (!tooth_present && !tooth_by_part) {
					record['treatments'].push(d);
					treatment_lines.push(record);
					surfaces.length = 0;
					console.log("Putttt 333============333")
					this.put_data(self_var, surfaces, selected_tooth_temp, false, false, false, false);
				} else {
				        record['treatments'].push(d);
					    treatment_lines.push(record);
					    surfaces.length = 0;
					    console.log("Putttt 444============444 for toooooooooooothpart")
				        selected_tooth_temp = toothmap_id;
						surfaces.push(tid);
						console.log("surface while in putdata",selected_tooth_temp );
						this.put_data(self_var, surfaces, selected_tooth_temp, '', 'planned', false, false);


				}
			}
		},
		get_treatment_charge : function(treatment_id) {
			var $def = $.Deferred();
//			new Model('product.product').call('get_treatment_charge', [treatment_id]).then(function(res) {
//				$def.resolve(res);
//			});
			rpc.query({
	                model: 'product.product',
	                method: 'get_treatment_charge',
	                args: [treatment_id],
	            })
	            .then(function(res){
	            	$def.resolve(res);
	           });
			return $def;
		},

		decrement_thread : function(selected_surf) {
			_.each(selected_surf, function(ss) {
				var prev_cnt = ($('#'+ss).attr('class').split(' ')[3]);
				var new_cnt = String(parseInt(prev_cnt) - 1);
				document.getElementById(ss).classList.remove(prev_cnt);
				document.getElementById(ss).classList.add(new_cnt);
			});
		},

		increment_thread : function(selected_surf) {
			_.each(selected_surf, function(ss) {
				var m = $('#' + ss).attr('class').split(' ');
				var prev_cnt = ($('#'+ss).attr('class').split(' ')[3]);
				var new_cnt = String(parseInt(prev_cnt) + 1);
				document.getElementById(ss).classList.remove(prev_cnt);
				document.getElementById(ss).classList.add(new_cnt);
			});
		},
		put_data_full_mouth : function(self_var, full_mouth_teeth_temp, full_mouth, selected_treatment_temp, status_to_define, mouth_part ,created_date, is_prev_record, other_history) {
			if (selected_treatment_temp.action == 'missing') {
				self_var.perform_missing_action(full_mouth_teeth_temp);
			}
			if (full_mouth) {
				var panned_text = $('#planned').text().trim();
				var status_to_define_temp = panned_text;
				var completed_text = $('#completed').text().trim();
				var inprogress_text = $('#in_progress').text().trim();
				var status_defined = status_to_define_temp.toLowerCase();
				if (status_to_define){
					if(status_to_define == 'completed'){
						status_to_define_temp = completed_text;
					}else if(status_to_define == 'in_progress'){
						status_to_define_temp = inprogress_text;
					}else if(status_to_define == 'planned'){
						status_to_define_temp = panned_text;
					}
				}
//				status_to_define_temp = status_to_define.substr(0, 1).toUpperCase() + status_to_define.substr(1);

				var today = new Date();
				if (created_date) {
					today = created_date;
				}
				var table_str = '';
				this.get_treatment_charge(selected_treatment_temp.treatment_id).then(function(t_charge) {
					console.log("Lineeeee 22222222222222222222222 ")

					if (!t_charge) {
						t_charge = '0.0';
					}
					operation_id += 1;
					var total_teeth = '';
					var surf_list = new Array();
					_.each(full_mouth_teeth_temp, function(each_full_mouth_teeth_temp) {
						total_teeth += '_' + each_full_mouth_teeth_temp;
						surf_list.push('view_' + each_full_mouth_teeth_temp + '_center');
						surf_list.push('view_' + each_full_mouth_teeth_temp + '_right');
						surf_list.push('view_' + each_full_mouth_teeth_temp + '_left');
						surf_list.push('view_' + each_full_mouth_teeth_temp + '_top');
						surf_list.push('view_' + each_full_mouth_teeth_temp + '_bottom');
					});
					if(surf_list){
					self_var.increment_thread(surf_list);
					}
					total_teeth = total_teeth.substr(1);
					if (other_history)
						table_str += '<tr class = ' + total_teeth + ' id = operation_' + operation_id + ' style = "display:none">';
					else
						table_str += '<tr class = ' + total_teeth + ' id = operation_' + operation_id + '>';
					table_str += '<td id = "date_time_' + operation_id + '">' + today + '</td>';
					table_str += '<td class = "' + selected_treatment_temp.treatment_id + '" ' + 'id = "desc_' + operation_id + '">' + selected_treatment_temp.treatment_name + '</td>';
					table_str += '<td class = "' + 'all' + '" id = "tooth_' + operation_id + '">' + '-' + '</td>';

					table_str += '<td id = "status_' + operation_id +'" status_name = "'+status_to_define+'">' + status_to_define_temp + '</td>';
					table_str += '<td id = "surface_' + operation_id + '">'+mouth_part+'</td>';

					table_str += '<td id = "dentist_' + operation_id + '">' + user_name + '</td>';
					table_str += '<td id = "amount_' + operation_id + '">' + t_charge + '</td>';
					table_str += '<td class = "progress_table_actions" id = "action_' + operation_id + '">' + selected_treatment_temp.action + '</td>';
					table_str += '<td class = "delete_td" id = "delete_' + operation_id + '">' + '<img src = "/pragtech_dental_management/static/src/img/delete.png" height = "20px" width = "20px"/>' + '</td>';
					table_str += '<td style = "display:none" id = "previous_' + operation_id + '">' + is_prev_record + '</td>';
					table_str += '</tr>';

					$('#progres_table').append(table_str);

					$('#delete_' + operation_id).click(function() {
						var x = window.confirm("Are you sure you want to delete?");
						if (x) {
							update = false;
							cont = false;
							var delStr = '';
							var actual_id = String(this.id).substr(7);
							actual_id = parseInt(actual_id);
							var tabel = document.getElementById('operations');
							var tr = document.getElementById('operation_' + actual_id);
							var tooth = document.getElementById('tooth_' + actual_id);
							var desc_class = $("#desc_" + actual_id).attr('class');
                            console.log('the tr is ',tr )


							var status = document.getElementById('status_' + actual_id);
							var status_name = $(status).attr('status_name')
							if (status_name == 'completed' || status_name == 'in_progress') {
								alert('Cannot delete');
							} else {
                                var action = document.getElementById('action_' + actual_id);
								var action_id = action.innerHTML;
								if(mouth_part == 'Full_mouth') {
								    var tooth_id = tr.className.split('_');
								    console.log('the tr ,tooth_idis ',tr ,tooth_id)
									var surf_list = new Array();
									_.each(full_mouth_teeth_temp, function(tooth_id) {
										surf_list.push('view_' + tooth_id + '_center');
										surf_list.push('view_' + tooth_id + '_right');
										surf_list.push('view_' + tooth_id + '_left');
										surf_list.push('view_' + tooth_id + '_top');
										surf_list.push('view_' + tooth_id + '_bottom');
									});
									self_var.decrement_thread(surf_list);


								self_var.remove_selection_action(tooth_id);
								if (action_id == 'missing') {
									self_var.remove_missing_action(tooth_id);
								}
							}
								tr.parentNode.removeChild(tr);

								if(mouth_part =='Upper_Jaw')
								delStr=localStorage.getItem('upperkeys');
								if(mouth_part =='Lower_Jaw')
								delStr=localStorage.getItem('lowerkeys');

								localStorage.setItem('toDel',delStr);

								//this.$el.find('#UT,#LT').mapster('set', false, delStr)

								localStorage.removeItem('upperkeys');
			                    localStorage.removeItem('lowerkeys');
							}

						}

					});

				});
				if (selected_treatment_temp.action == false) {
				}
			}
		},
		put_data_toothpart : function(self_var, selected_tooth_temp, selected_surface ,tooth_by_part, selected_treatment_temp, status_to_define, created_date, is_prev_record, other_history) {
            console.log("inside toothpart fn printing selected_tooth_temp",selected_tooth_temp)
			if (tooth_by_part) {
			     var ts = selected_surface ;
                 var tooth_surface = ts.slice(0,-3);

				var panned_text = $('#planned').text().trim();
				var status_to_use = panned_text;
				var status_to_define_temp = panned_text;
				var completed_text = $('#completed').text().trim();
				var inprogress_text = $('#in_progress').text().trim();
				var status_defined = status_to_define_temp.toLowerCase();
				if (status_to_define){
					if(status_to_define == 'completed'){
						status_to_define_temp = completed_text;
					}else if(status_to_define == 'in_progress'){
						status_to_define_temp = inprogress_text;
					}else if(status_to_define == 'planned'){
						status_to_define_temp = panned_text;
					}
				}
//				status_to_define_temp = status_to_define.substr(0, 1).toUpperCase() + status_to_define.substr(1);
				var today = new Date();
				if (created_date) {
					today = created_date;
				}
				var table_str = '';
				this.get_treatment_charge(selected_treatment_temp.treatment_id).then(function(t_charge) {
					console.log("Lineeeee 22222222222222222222222  toothpartfn")

					if (!t_charge) {
						t_charge = '0.0';
					}
					operation_id += 1;

				if (other_history)
					table_str += '<tr id = operation_' + operation_id + ' style= "display:none">';
				else
				table_str += '<tr id = operation_' + operation_id + '>';
				table_str += '<td id = "date_time_' + operation_id + '">' + today + '</td>';
				table_str += '<td class = "' + selected_treatment_temp.treatment_id + '" ' + 'id = "desc_' + operation_id + '">' + selected_treatment_temp.treatment_name + '</td>';

                    if (type == 'palmer') {

                        var numbers = parseInt(selected_tooth_temp);
                            if (selected_tooth_temp == '-') {
                                numbers = '-';
                            }
                        switch(numbers) {
                        case 1:
                            table_str += '<td class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Palmer[1] + '</td>';
                            break;
                        case 2:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[2] + '</td>';
                            break;
                        case 3:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[3] + '</td>';
                            break;
                        case 4:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[4] + '</td>';
                            break;
                        case 5:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[5] + '</td>';
                            break;
                        case 6:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[6] + '</td>';
                            break;
                        case 7:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[7] + '</td>';
                            break;
                        case 8:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[8] + '</td>';
                            break;
                        case 9:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[9] + '</td>';
                            break;
                        case 10:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[10] + '</td>';
                            break;
                        case 11:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[11] + '</td>';
                            break;
                        case 12:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[12] + '</td>';
                            break;
                        case 13:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[13] + '</td>';
                            break;
                        case 14:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[14] + '</td>';
                            break;
                        case 15:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[15] + '</td>';
                            break;
                        case 16:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[16] + '</td>';
                            break;
                        case 17:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[17] + '</td>';
                            break;
                        case 18:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[18] + '</td>';
                            break;
                        case 19:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[19] + '</td>';
                            break;
                        case 20:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[20] + '</td>';
                            break;
                        case 21:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[21] + '</td>';
                            break;
                        case 22:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[22] + '</td>';
                            break;
                        case 23:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[23] + '</td>';
                            break;
                        case 24:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[24] + '</td>';
                            break;
                        case 25:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[25] + '</td>';
                            break;
                        case 26:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[26] + '</td>';
                            break;
                        case 27:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[27] + '</td>';
                            break;
                        case 28:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[28] + '</td>';
                            break;
                        case 29:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[29] + '</td>';
                            break;
                        case 30:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[30] + '</td>';
                            break;
                        case 31:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[31] + '</td>';
                            break;
                        case 32:
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[32] + '</td>';
                            break;
                        case '-':
                            table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + '-' + '</td>';
                            break;

                        }
                    } else if (type == 'universal') {
                        table_str += '<td class = "' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + selected_tooth_temp + '</td>';
                    } else if (type == 'iso') {
                        var numbers = parseInt(selected_tooth_temp);

                        switch(numbers) {
                        case 1:
                            table_str += '<td class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[1] + '</td>';
                            break;
                        case 2:
                            table_str += '<td class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[2] + '</td>';
                            break;
                        case 3:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[3] + '</td>';
                            break;
                        case 4:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[4] + '</td>';
                            break;
                        case 5:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[5] + '</td>';
                            break;
                        case 6:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[6] + '</td>';
                            break;
                        case 7:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[7] + '</td>';
                            break;
                        case 8:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[8] + '</td>';
                            break;
                        case 9:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[9] + '</td>';
                            break;
                        case 10:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[10] + '</td>';
                            break;
                        case 11:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[11] + '</td>';
                            break;
                        case 12:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[12] + '</td>';
                            break;
                        case 13:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[13] + '</td>';
                            break;
                        case 14:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[14] + '</td>';
                            break;
                        case 15:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[15] + '</td>';
                            break;
                        case 16:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[16] + '</td>';
                            break;
                        case 17:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[17] + '</td>';
                            break;
                        case 18:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[18] + '</td>';
                            break;
                        case 19:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[19] + '</td>';
                            break;
                        case 20:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[20] + '</td>';
                            break;
                        case 21:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[21] + '</td>';
                            break;
                        case 22:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[22] + '</td>';
                            break;
                        case 23:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[23] + '</td>';
                            break;
                        case 24:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[24] + '</td>';
                            break;
                        case 25:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[25] + '</td>';
                            break;
                        case 26:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[26] + '</td>';
                            break;
                        case 27:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[27] + '</td>';
                            break;
                        case 28:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[28] + '</td>';
                            break;
                        case 29:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[29] + '</td>';
                            break;
                        case 30:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[30] + '</td>';
                            break;
                        case 31:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[31] + '</td>';
                            break;
                        case 32:
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[32] + '</td>';
                            break;
                        case '-':
                            table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + '-' + '</td>';
                            break;

                        }
                    }
				table_str += '<td id = "status_' + operation_id +'" status_name = "'+status_defined+'">' + status_to_use + '</td>';
                table_str += '<td id = "surface_' + operation_id + '">' + tooth_surface + '</td>';
				table_str += '<td id = "dentist_' + operation_id + '">' + user_name + '</td>';
				table_str += '<td id = "amount_' + operation_id + '">' + t_charge + '</td>';
				table_str += '<td class = "progress_table_actions" id = "action_' + operation_id + '">' + selected_treatment_temp.action + '</td>';
				table_str += '<td class = "delete_td" id = "delete_' + operation_id + '">' + '<img src = "/pragtech_dental_management/static/src/img/delete.png" height = "20px" width = "20px"/>' + '</td>';
				table_str += '<td style = "display:none" id = "previous_' + operation_id + '">' + is_prev_record + '</td>';
				table_str += '</tr>';

					$('#progres_table').append(table_str);

					$('#delete_' + operation_id).click(function() {
						var x = window.confirm("Are you sure you want to delete?");

						if (x) {
						console.log("inside put_data_toothpart")
							update = false;
							cont = false;
							var actual_id = String(this.id).substr(7);
							console.log(String(this.id).substr(7))
							actual_id = parseInt(actual_id);
							var tabel = document.getElementById('operations');
							var tr = document.getElementById('operation_' + actual_id);
							var tooth = document.getElementById('tooth_' + actual_id);

							var desc_class = $("#desc_" + actual_id).attr('class');

							var tooth_id = tr.className.split('_');
                            console.log("document.getElementById('tooth_' + actual_id);  and tooth_id in del" + tooth +','+tooth_id)
							var status = document.getElementById('status_' + actual_id);
							var status_name = $(status).attr('status_name')
							if (status_name == 'completed' || status_name == 'in_progress') {
								alert('Cannot delete');
							} else {

							    localStorage.setItem('toDel',selected_surface);


//								var action = document.getElementById('action_' + actual_id);
//								var action_id = action.innerHTML;
//								{
//									var surf_list = new Array();
//									_.each(full_mouth_teeth_temp, function(tooth_id) {
//										surf_list.push('view_' + tooth_id + '_center');
//										surf_list.push('view_' + tooth_id + '_right');
//										surf_list.push('view_' + tooth_id + '_left');
//										surf_list.push('view_' + tooth_id + '_top');
//										surf_list.push('view_' + tooth_id + '_bottom');
//									});
//									self_var.decrement_thread(surf_list);
//								}
//								self_var.remove_selection_action(tooth_id);
//								if (action_id == 'missing') {
//									self_var.remove_missing_action(tooth_id);
//								}
								tr.parentNode.removeChild(tr);

							}

						}

					});

				});
				if (selected_treatment_temp.action == false) {
				}
				tooth_by_part = 0;
			}
		},
		put_data : function(self_var, surfaces, selected_tooth_temp, selected_surface_temp, status_defined, created_date, is_prev_record, other_history) {
		    console.log("inside put_data")
			console.log("SUrfacesssssssssssss   ,selected_surface_temp,tooth_by_part  ",surfaces, selected_surface_temp, tooth_by_part)

			if (!selected_tooth_temp) {
				selected_tooth_temp = '-';
			}
			var selected_treatment_temp = selected_treatment;
			var table_str = '';
			var today = new Date();
			if (created_date) {
				today = created_date;
			}
			console.log("Statussssssssss defineddddddddddddddddd   ",status_defined)
			var panned_text = $('#planned').text().trim();
			console.log("Put dataaa   ",panned_text)
			var status_to_use = panned_text;
			var completed_text = $('#completed').text().trim()
			var inprogress_text = $('#in_progress').text().trim()
			if (status_defined)
				if(status_defined == 'completed'){
					status_to_use = completed_text;
				}else if(status_defined == 'in_progress'){
					status_to_use = inprogress_text;
				}else if(status_defined == 'planned'){
					status_to_use = panned_text;
				}
			if (status_to_use == 'planned'){
				status_to_use = panned_text;
//				status_to_use = status_to_use.substr(0, 1).toUpperCase() + status_to_use.substr(1);
			}
			console.log("_________________________  ",status_to_use)
			this.get_treatment_charge(selected_treatment_temp.treatment_id).then(function(t_charge) {
				if (!t_charge) {
					t_charge = '0.0';
				}
				console.log("Line 33333333333333333333=======")
				operation_id += 1;
				var found = self_var.$el.find('.selected_operation');
				if (found) {
					found.removeClass("selected_operation");
				}
				if (other_history)
					table_str += '<tr id = operation_' + operation_id + ' style= "display:none">';
				else
					table_str += '<tr id = operation_' + operation_id + '>';
				table_str += '<td id = "date_time_' + operation_id + '">' + today + '</td>';
				table_str += '<td class = "' + selected_treatment_temp.treatment_id + '" ' + 'id = "desc_' + operation_id + '">' + selected_treatment_temp.treatment_name + '</td>';

				if (type == 'palmer') {

					var numbers = parseInt(selected_tooth_temp);

					if (selected_tooth_temp == '-') {
						numbers = '-';
					}
					switch(numbers) {
					case 1:
						table_str += '<td class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Palmer[1] + '</td>';
						break;
					case 2:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[2] + '</td>';
						break;
					case 3:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[3] + '</td>';
						break;
					case 4:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[4] + '</td>';
						break;
					case 5:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[5] + '</td>';
						break;
					case 6:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[6] + '</td>';
						break;
					case 7:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[7] + '</td>';
						break;
					case 8:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[8] + '</td>';
						break;
					case 9:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[9] + '</td>';
						break;
					case 10:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[10] + '</td>';
						break;
					case 11:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[11] + '</td>';
						break;
					case 12:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[12] + '</td>';
						break;
					case 13:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[13] + '</td>';
						break;
					case 14:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[14] + '</td>';
						break;
					case 15:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[15] + '</td>';
						break;
					case 16:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[16] + '</td>';
						break;
					case 17:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[17] + '</td>';
						break;
					case 18:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[18] + '</td>';
						break;
					case 19:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[19] + '</td>';
						break;
					case 20:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[20] + '</td>';
						break;
					case 21:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[21] + '</td>';
						break;
					case 22:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[22] + '</td>';
						break;
					case 23:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[23] + '</td>';
						break;
					case 24:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[24] + '</td>';
						break;
					case 25:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[25] + '</td>';
						break;
					case 26:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[26] + '</td>';
						break;
					case 27:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[27] + '</td>';
						break;
					case 28:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[28] + '</td>';
						break;
					case 29:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[29] + '</td>';
						break;
					case 30:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[30] + '</td>';
						break;
					case 31:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[31] + '</td>';
						break;
					case 32:
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[32] + '</td>';
						break;
					case '-':
						table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + '-' + '</td>';
						break;

					}
				} else if (type == 'universal') {
					table_str += '<td class = "' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + selected_tooth_temp + '</td>';
				} else if (type == 'iso') {
					var numbers = parseInt(selected_tooth_temp);

					switch(numbers) {
					case 1:
						table_str += '<td class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[1] + '</td>';
						break;
					case 2:
						table_str += '<td class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[2] + '</td>';
						break;
					case 3:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[3] + '</td>';
						break;
					case 4:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[4] + '</td>';
						break;
					case 5:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[5] + '</td>';
						break;
					case 6:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[6] + '</td>';
						break;
					case 7:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[7] + '</td>';
						break;
					case 8:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[8] + '</td>';
						break;
					case 9:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[9] + '</td>';
						break;
					case 10:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[10] + '</td>';
						break;
					case 11:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[11] + '</td>';
						break;
					case 12:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[12] + '</td>';
						break;
					case 13:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[13] + '</td>';
						break;
					case 14:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[14] + '</td>';
						break;
					case 15:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[15] + '</td>';
						break;
					case 16:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[16] + '</td>';
						break;
					case 17:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[17] + '</td>';
						break;
					case 18:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[18] + '</td>';
						break;
					case 19:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[19] + '</td>';
						break;
					case 20:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[20] + '</td>';
						break;
					case 21:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[21] + '</td>';
						break;
					case 22:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[22] + '</td>';
						break;
					case 23:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[23] + '</td>';
						break;
					case 24:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[24] + '</td>';
						break;
					case 25:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[25] + '</td>';
						break;
					case 26:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[26] + '</td>';
						break;
					case 27:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[27] + '</td>';
						break;
					case 28:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[28] + '</td>';
						break;
					case 29:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[29] + '</td>';
						break;
					case 30:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[30] + '</td>';
						break;
					case 31:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[31] + '</td>';
						break;
					case 32:
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[32] + '</td>';
						break;
					case '-':
						table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + '-' + '</td>';
						break;

					}
				}
				table_str += '<td id = "status_' + operation_id +'" status_name = "'+status_defined+'">' + status_to_use + '</td>';

               if(!tooth_by_part){
				table_str += '<td id = "surface_' + operation_id + '">';
				_.each(surfaces, function(each_surf) {
					table_str += each_surf + ' ';
				});
				self_var.increment_thread(selected_surface_temp);
				table_str += '</td>';
                }else{
                table_str += '<td id = "surface_' + operation_id + '">' +surfaces+'</td>';

		        tooth_by_part == 0;
                }

				table_str += '<td id = "dentist_' + operation_id + '">' + user_name + '</td>';
				table_str += '<td id = "amount_' + operation_id + '">' + t_charge + '</td>';
				table_str += '<td class = "progress_table_actions" id = "action_' + operation_id + '">' + selected_treatment_temp.action + '</td>';
				table_str += '<td class = "delete_td" id = "delete_' + operation_id + '">' + '<img src = "/pragtech_dental_management/static/src/img/delete.png" height = "20px" width = "20px"/>' + '</td>';
				table_str += '<td style = "display:none" id = "previous_' + operation_id + '">' + is_prev_record + '</td>';
				table_str += '</tr>';

				$('#progres_table').append(table_str);
				$('#operation_' + operation_id).click(function() {
					var found = self_var.$el.find('.selected_operation');
					if (found) {
						found.removeClass("selected_operation");
					}
					$(this).attr('class', 'selected_operation');
				});
				$('#delete_' + operation_id).click(function() {
					var x = window.confirm("Are you sure you want to delete?");
					if (x) {
					console.log("del of putdata");
						update = false;
						cont = false;
						var actual_id = String(this.id).substr(7);
						actual_id = parseInt(actual_id);
						var tabel = document.getElementById('operations');
						var tr = document.getElementById('operation_' + actual_id);
						var tooth = document.getElementById('tooth_' + actual_id);
						var desc_class = $("#desc_" + actual_id).attr('class');

						var tooth_id = $(tooth).attr('class');

						var status = document.getElementById('status_' + actual_id);
						var status_name = $(status).attr('status_name')
						if (status_name == 'completed' || status_name == 'in_progress') {
							alert('Cannot delete');
						}else {
							var action = document.getElementById('action_' + actual_id);
							var action_id = action.innerHTML; {
								var surface_vals = ($('#surface_' + actual_id).text()).split(' ');
								var surf_list = new Array();
								_.each(surface_vals, function(sv) {
									if ($('#view_' + tooth_id + '_center').attr('class').split(' ')[1] == sv) {
										surf_list.push('view_' + tooth_id + '_center');
									}
									if ($('#view_' + tooth_id + '_right').attr('class').split(' ')[1] == sv) {
										surf_list.push('view_' + tooth_id + '_right');
									}
									if ($('#view_' + tooth_id + '_left').attr('class').split(' ')[1] == sv) {
										surf_list.push('view_' + tooth_id + '_left');
									}
									if ($('#view_' + tooth_id + '_top').attr('class').split(' ')[1] == sv) {
										surf_list.push('view_' + tooth_id + '_top');
									}
									if ($('#view_' + tooth_id + '_bottom').attr('class').split(' ')[1] == sv) {
										surf_list.push('view_' + tooth_id + '_bottom');
									}
								});
								self_var.decrement_thread(surf_list);
							}
							if (action_id == 'missing') {
								$($("#" + $('#' + tooth_id).attr('id')).css('visibility', "visible").attr('class', 'teeth'));
								$("#view_" + $('#' + tooth_id).attr('id') + "_top,#view_" + $('#' + tooth_id).attr('id') + "_left,#view_" + $('#' + tooth_id).attr('id') + "_bottom,#view_" + $('#' + tooth_id).attr('id') + "_right,#view_" + $('#' + tooth_id).attr('id') + "_center").attr('visibility', 'visible');
								$("#view_" + $('#' + tooth_id).attr('id') + "_top,#view_" + $('#' + tooth_id).attr('id') + "_left,#view_" + $('#' + tooth_id).attr('id') + "_bottom,#view_" + $('#' + tooth_id).attr('id') + "_right,#view_" + $('#' + tooth_id).attr('id') + "_center").attr('fill', 'white');
							} else {

								if (parseInt(($('#view_' + tooth_id + '_bottom').attr('class')).split(' ')[3]) == 0)
									$("#" + $('#view_' + tooth_id + '_bottom').attr('id')).attr('fill', 'white');
								if (parseInt(($('#view_' + tooth_id + '_right').attr('class')).split(' ')[3]) == 0)
									$("#" + $('#view_' + tooth_id + '_right').attr('id')).attr('fill', 'white');
								if (parseInt(($('#view_' + tooth_id + '_center').attr('class')).split(' ')[3]) == 0)
									$("#" + $('#view_' + tooth_id + '_center').attr('id')).attr('fill', 'white');
								if (parseInt(($('#view_' + tooth_id + '_left').attr('class')).split(' ')[3]) == 0)
									$("#" + $('#view_' + tooth_id + '_left').attr('id')).attr('fill', 'white');
								if (parseInt(($('#view_' + tooth_id + '_top').attr('class')).split(' ')[3]) == 0)
									$("#" + $('#view_' + tooth_id + '_top').attr('id')).attr('fill', 'white');
							}
                                console.log("the surface value is ",surfaces);
                                localStorage.setItem('toDel',surfaces);

							tr.parentNode.removeChild(tr);
							for (var index = 0; index < treatment_lines.length; index++) {
								if (treatment_lines[index].tooth_id == tooth_id) {
									for (var i2 = 0; i2 < treatment_lines[index].treatments.length; i2++) {
										if (treatment_lines[index].treatments[i2].treatment_id == parseInt(desc_class)) {
											treatment_lines.splice(index, 1);
											operation_id += 1;
											var found = self_var.$el.find('.selected_treatment_temp');
											if (found) {
												found.removeClass("selected_treatment_temp");
											}
											return;
										}
									}
								}
							}

						}

					}

				});
			});

		},
		get_treatment_cats : function() {
			var $def = $.Deferred();
			var self = this;
//			new Model('product.category').call('get_treatment_categs', [self.patient_id]).then(function(treatment_list) {
//				$def.resolve(treatment_list);
//			});
			rpc.query({
                model: 'product.category',
                method: 'get_treatment_categs',
                args: [self.patient_id],
            })
            .then(function(treatment_list) {
            	$def.resolve(treatment_list);
            });
			return $def;
		},

		patient_history : function() {
			var $def = $.Deferred();
			var self = this;
			if (!self.patient_id) {
				alert('Session Expired!!');
				window.location = '/web';
			}
//			new Model('medical.patient').call('get_patient_history', [self.patient_id, self.appointment_id]).then(function(patient_history) {
//				Missing_Tooth = patient_history[0];
//				patient_history.splice(0, 1);
//				other_patient_history = patient_history;
//				$def.resolve(patient_history);
//			});
			rpc.query({
                model: 'medical.patient',
                method: 'get_patient_history',
                args: [self.patient_id, self.appointment_id],
            })
            .then(function(patient_history) {
            	Missing_Tooth = patient_history[0];
				patient_history.splice(0, 1);
				other_patient_history = patient_history;
				$def.resolve(patient_history);
            });

			return $def;
		},
		get_user : function(uid) {
//			new Model('res.partner').call('get_user_name', [uid]).then(function(uname) {
//				user_name = uname;
//			});
			rpc.query({
                model: 'res.partner',
                method: 'get_user_name',
                args: [uid],
            })
            .then(function(uname) {
            	user_name = uname;
            });
		},

		displaySVGBox : function(chartoption){
		console.log("entering chart area")
		if(chartoption=='adult'){ var cnt = 1;
				var cnt2 = 1;
				var surface2_cnt = 32;
				var tooth2_cnt = 32;
				for (var t = 1; t <= NO_OF_TEETH; t++) {
					var NS = 'http://www.w3.org/2000/svg';
					var svg = $('#svg_object')[0];

					if (cnt <= 16) {//devided teeths into 2 sections
						var path1_1 = 34.95833333333337;
						var path1_2 = 21.250000000000007;
						var path2_1 = 25.513888888888914;
						var path2_2 = 31.875000000000007;
						var path3_1 = 34.95833333333337;
						var path3_2 = 46.04166666666665;
						var path4_1 = 52.666666666666686;
						var path4_2 = 31.875000000000007;
						var path5_1 = 34.958333333333385;
						var path5_2 = 31.875000000000007;

						//var source_img = '<img class = "teeth" src = "/pragtech_dental_management/static/src/img/tooth' + t + '.png" id = ' + t + ' width = "46" height = "50"/>';
						var missing = 0;
						for (var m = 0; m < Missing_Tooth.length; m++) {
							if (t == Missing_Tooth[m]) {
								missing = 1;
								// var source_img = '<img class = "blank" src = "/pragtech_dental_management/static/src/img/images.png" id = ' + t + ' width = "46" height = "50"/>';
								var source_img = '<img class = "blank" src = "/pragtech_dental_management/static/src/img/tooth' + t + '.png" id = ' + t + ' width = "46" height = "50" style="visibility:hidden"/>';
							}
						}

					//	$("#teeth-surface-1").append(source_img);
						if (cnt == 1) {//hardcode first rectangular coordinates
							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view buccal " + cnt + '_buccal 0');
							newElement.setAttribute("id", "view_" + cnt + "_top");

							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + path1_1 + " " + path1_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + path2_1 + " " + path2_2 + ")");
							newElement.setAttribute("class", "view distal " + cnt + '_distal 0');
							newElement.setAttribute("id", "view_" + cnt + "_left");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view lingual " + cnt + '_lingual 0');
							newElement.setAttribute("id", "view_" + cnt + "_bottom");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + path3_1 + " " + path3_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view mesial " + cnt + '_mesial 0');
							newElement.setAttribute("id", "view_" + cnt + "_right");
							newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + path4_1 + " " + path4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view occlusal " + cnt + '_occlusal 0');
							newElement.setAttribute("id", "view_" + cnt + "_center");
							newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + path5_1 + " " + path5_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

						} else {
							var top,
							    bottom,
							    right,
							    left,
							    center;
							if (cnt <= 5) {
								top = 'buccal';
								right = 'mesial';
								bottom = 'lingual';
								left = 'distal';
								center = 'occlusal';
							} else if (cnt <= 11) {
								top = 'labial';
								right = 'mesial';
								bottom = 'lingual';
								left = 'distal';
								center = 'incisal';
							} else if (cnt <= 16) {
								top = 'buccal';
								right = 'distal';
								bottom = 'lingual';
								left = 'mesial';
								center = 'occlusal';
							}
							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + top + " " + cnt + '_' + top + ' 0');
							newElement.setAttribute("id", "view_" + cnt + "_top");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path1_1 + (46 * (cnt - 1))) + " " + path1_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + left + " " + cnt + '_' + left + ' 0');
							newElement.setAttribute("id", "view_" + cnt + "_left");
							newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path2_1 + (46 * (cnt - 1))) + " " + path2_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + bottom + " " + cnt + '_' + bottom + ' 0');
							newElement.setAttribute("id", "view_" + cnt + "_bottom");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path3_1 + (46 * (cnt - 1))) + " " + path3_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + right + " " + cnt + '_' + right + ' 0');
							newElement.setAttribute("id", "view_" + cnt + "_right");
							newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path4_1 + (46 * (cnt - 1))) + " " + path4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + center + " " + cnt + '_' + center + ' 0');
							newElement.setAttribute("id", "view_" + cnt + "_center");
							newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path1_1 + (46 * (cnt - 1))) + " " + path4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

						}
						if (missing) {
							$("#view_" + cnt + "_top,#view_" + cnt + "_left,#view_" + cnt + "_bottom,#view_" + cnt + "_right,#view_" + cnt + "_center").attr('visibility', 'hidden');
						}
					} else {
						var p1_1 = 33.998659373659635;
						var p1_2 = 69.01321857571864;
						var p2_1 = 24.554214929215078;
						var p2_2 = 79.63821857571861;
						var p3_1 = 33.998659373659635;
						var p3_2 = 93.80488524238524;
						var p4_1 = 51.706992706992764;
						var p4_2 = 79.63821857571861;

					//	var source_img = '<img class = "teeth" src = "/pragtech_dental_management/static/src/img/tooth' + tooth2_cnt + '.png" id = ' + tooth2_cnt + ' width = "46" height = "50"/>';

						var missing = 0;
						for (var m = 0; m < Missing_Tooth.length; m++) {
							if (tooth2_cnt == Missing_Tooth[m]) {
								missing = 1;
								// var source_img = '<img class = "blank" src = "/pragtech_dental_management/static/src/img/images.png" id = ' + tooth2_cnt + ' width = "46" height = "50"/>';
								var source_img = '<img class = "blank" src = "/pragtech_dental_management/static/src/img/tooth' + tooth2_cnt + '.png" id = ' + tooth2_cnt + ' width = "46" height = "50" style="visibility:hidden"/>';
							}
						}
						//$("#teeth-surface-2").append(source_img);
						if (cnt == 17) {//hardcode first rectangular coordinates
							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view lingual " + surface2_cnt + '_lingual 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_top");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + p1_1 + " " + p1_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view distal " + surface2_cnt + '_distal 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_left");
							newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + p2_1 + " " + p2_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view buccal " + surface2_cnt + '_buccal 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_bottom");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + p3_1 + " " + p3_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view mesial " + surface2_cnt + '_mesial 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_right");
							newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + p4_1 + " " + p4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view occlusal " + surface2_cnt + '_occlusal 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_center");
							newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + p1_1 + " " + p4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

						} else {
							var top,
							    bottom,
							    right,
							    left,
							    center;
							if (surface2_cnt <= 21) {
								top = 'lingual';
								right = 'distal';
								bottom = 'buccal';
								left = 'mesial';
								center = 'occlusal';
							} else if (surface2_cnt <= 27) {
								top = 'lingual';
								right = 'mesial';
								bottom = 'labial';
								left = 'distal';
								center = 'incisal';
							} else {
								top = 'lingual';
								right = 'mesial';
								bottom = 'buccal';
								left = 'distal';
								center = 'occlusal';
							}
							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + top + " " + surface2_cnt + "_" + top + ' 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_top");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path1_1 + (46 * (cnt2 - 1)) - 1)) + " " + p1_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + left + " " + surface2_cnt + "_" + left + ' 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_left");
							newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path2_1 + (46 * (cnt2 - 1)) - 1)) + " " + p2_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + bottom + " " + surface2_cnt + "_" + bottom + ' 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_bottom");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path3_1 + (46 * (cnt2 - 1)) - 1)) + " " + p3_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + right + " " + surface2_cnt + "_" + right + ' 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_right");
							newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path4_1 + (46 * (cnt2 - 1)) - 1)) + " " + p4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + center + " " + surface2_cnt + "_" + center + ' 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_center");
							newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path1_1 + (46 * (cnt2 - 1)) - 1)) + " " + p4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);
						}
						if (missing) {
							$("#view_" + surface2_cnt + "_top,#view_" + surface2_cnt + "_left,#view_" + surface2_cnt + "_bottom,#view_" + surface2_cnt + "_right,#view_" + surface2_cnt + "_center").attr('visibility', 'hidden');
						}
						surface2_cnt -= 1;
						tooth2_cnt -= 1;
						cnt2++;
					}
					cnt++;
				}
				}
		if(chartoption=='child'){
		var cnt = 1;
var cnt2 = 1;
var surface2_cnt = 20;
var tooth2_cnt = 20;
for (var t = 1; t <= 20; t++) {
					var NS = 'http://www.w3.org/2000/svg';
					var svg = $('#svg_object_child')[0];

					if (cnt <= 10) {//devided teeths into 2 sections
						var path1_1 = 34.95833333333337;
						var path1_2 = 21.250000000000007;
						var path2_1 = 25.513888888888914;
						var path2_2 = 31.875000000000007;
						var path3_1 = 34.95833333333337;
						var path3_2 = 46.04166666666665;
						var path4_1 = 52.666666666666686;
						var path4_2 = 31.875000000000007;
						var path5_1 = 34.958333333333385;
						var path5_2 = 31.875000000000007;


						if (cnt == 1) {//hardcode first rectangular coordinates
							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view buccal " + cnt + '_buccal 0');
							newElement.setAttribute("id", "view_" + cnt + "_top");

							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + path1_1 + " " + path1_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + path2_1 + " " + path2_2 + ")");
							newElement.setAttribute("class", "view distal " + cnt + '_distal 0');
							newElement.setAttribute("id", "view_" + cnt + "_left");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view lingual " + cnt + '_lingual 0');
							newElement.setAttribute("id", "view_" + cnt + "_bottom");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + path3_1 + " " + path3_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view mesial " + cnt + '_mesial 0');
							newElement.setAttribute("id", "view_" + cnt + "_right");
							newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + path4_1 + " " + path4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view occlusal " + cnt + '_occlusal 0');
							newElement.setAttribute("id", "view_" + cnt + "_center");
							newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + path5_1 + " " + path5_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

						} else {
							var top,
							    bottom,
							    right,
							    left,
							    center;
							if (cnt <= 5) {
								top = 'buccal';
								right = 'mesial';
								bottom = 'lingual';
								left = 'distal';
								center = 'occlusal';
							} else  {
								top = 'labial';
								right = 'mesial';
								bottom = 'lingual';
								left = 'distal';
								center = 'incisal';
							}
							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + top + " " + cnt + '_' + top + ' 0');
							newElement.setAttribute("id", "view_" + cnt + "_top");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path1_1 + (46 * (cnt - 1))) + " " + path1_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + left + " " + cnt + '_' + left + ' 0');
							newElement.setAttribute("id", "view_" + cnt + "_left");
							newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path2_1 + (46 * (cnt - 1))) + " " + path2_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + bottom + " " + cnt + '_' + bottom + ' 0');
							newElement.setAttribute("id", "view_" + cnt + "_bottom");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path3_1 + (46 * (cnt - 1))) + " " + path3_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + right + " " + cnt + '_' + right + ' 0');
							newElement.setAttribute("id", "view_" + cnt + "_right");
							newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path4_1 + (46 * (cnt - 1))) + " " + path4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + center + " " + cnt + '_' + center + ' 0');
							newElement.setAttribute("id", "view_" + cnt + "_center");
							newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path1_1 + (46 * (cnt - 1))) + " " + path4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

						}

					} else {
						var p1_1 = 33.998659373659635;
						var p1_2 = 69.01321857571864;
						var p2_1 = 24.554214929215078;
						var p2_2 = 79.63821857571861;
						var p3_1 = 33.998659373659635;
						var p3_2 = 93.80488524238524;
						var p4_1 = 51.706992706992764;
						var p4_2 = 79.63821857571861;


						if (cnt == 11) {//hardcode first rectangular coordinates
							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view lingual " + surface2_cnt + '_lingual 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_top");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + p1_1 + " " + p1_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view distal " + surface2_cnt + '_distal 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_left");
							newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + p2_1 + " " + p2_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view buccal " + surface2_cnt + '_buccal 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_bottom");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + p3_1 + " " + p3_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view mesial " + surface2_cnt + '_mesial 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_right");
							newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + p4_1 + " " + p4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view occlusal " + surface2_cnt + '_occlusal 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_center");
							newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + p1_1 + " " + p4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

						} else {
							var top,
							    bottom,
							    right,
							    left,
							    center;
							if (surface2_cnt <= 15) {
								top = 'lingual';
								right = 'mesial';
								bottom = 'labial';
								left = 'distal';
								center = 'incisal';
							} else {
								top = 'lingual';
								right = 'mesial';
								bottom = 'buccal';
								left = 'distal';
								center = 'occlusal';
							}
							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + top + " " + surface2_cnt + "_" + top + ' 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_top");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path1_1 + (46 * (cnt2 - 1)) - 1)) + " " + p1_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + left + " " + surface2_cnt + "_" + left + ' 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_left");
							newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path2_1 + (46 * (cnt2 - 1)) - 1)) + " " + p2_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + bottom + " " + surface2_cnt + "_" + bottom + ' 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_bottom");
							newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path3_1 + (46 * (cnt2 - 1)) - 1)) + " " + p3_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + right + " " + surface2_cnt + "_" + right + ' 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_right");
							newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path4_1 + (46 * (cnt2 - 1)) - 1)) + " " + p4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);

							var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
							newElement.setAttribute("class", "view " + center + " " + surface2_cnt + "_" + center + ' 0');
							newElement.setAttribute("id", "view_" + surface2_cnt + "_center");
							newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
							newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path1_1 + (46 * (cnt2 - 1)) - 1)) + " " + p4_2 + ")");
							newElement.setAttribute("fill", "white");
							newElement.setAttribute("stroke", "black");
							svg.appendChild(newElement);
						}

						surface2_cnt -= 1;
						tooth2_cnt -= 1;
						cnt2++;
					}
					cnt++;
				}
			}

		},

	});

	core.action_registry.add('dental_chart', DentalChartView);

	return {
		DentalChartView : DentalChartView,
	};

});
