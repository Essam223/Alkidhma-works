$(document).ready(function() {
var getKeySelectedArray = '';
var upkey = '';
var lowkey = '';
var childupkey = '';
var childlowkey = '';
var status = '';

status=localStorage.getItem('status');
console.log("entering mapkeys document  ",status);
if(!status)
{
localStorage.removeItem('test');
localStorage.removeItem('upperkeys');
localStorage.removeItem('lowerkeys');
localStorage.setItem('status','0')
}


$(document).on('click', '.delete_td', function(){
    console.log('here');
    var toRemove = localStorage.getItem('toDel');
    console.log('..........to be unselected.....ee',toRemove);

    var val, new_val, toRemove2=toRemove.split(","), temp = [];
    _.each(toRemove2, function(item) {
        try {
        	console.log("_______in remove 28_________",item);
            new_val = item.split("_");
            val = new_val[1];
            console.log("new_vals_________________",new_val,val)
            if (new_val[0] == 'toothcap' &&
                val && parseInt(val) < 10) {
                var t = new_val[0] + "_" + parseInt(val);
                temp.push(t);
            }
            else {
                temp.push(item);
            }
        }
        catch (err) {}
    });
    toRemove = temp;


    console.log('..........to be unselected.....ee',toRemove,this);
    image1.mapster('set', false, toRemove);
    image2.mapster('set', false, toRemove);
    image3.mapster('set', false, toRemove);
    image4.mapster('set', false, toRemove);
    $('#view_4_bottom').attr('fill', 'white');
//    image2.setAttribute("fill", "white");
});

//$("input[name$='checkfield']").change(function() {alert('helooooooooo')});
//
//$("#mapchk").on('change', function() {
//    alert("triggered!");
//});



$(document).on("change", "input[type=checkbox]", function(e) {
    console.log("inside checkbox fn")
    var checked = $("input[type=checkbox]:checked");
    var checkedValues = checked.map(function(i) { return $(this).val() }).get()
    var chkstr = checkedValues.join();
    if ($('#select_upper_mouth:checked').length == 0) {
        upkey = localStorage.getItem('upperkeys');
        image1.mapster('set', false, upkey);
    }
    if ($('#select_lower_mouth:checked').length == 0) {
        lowkey = localStorage.getItem('lowerkeys');
        image2.mapster('set', false, lowkey);
    }
    if ($('#select_upper_mouth_child:checked').length == 0) {
        childupkey = localStorage.getItem('childupperkeys');
        image3.mapster('set', false, childupkey);
    }
    if ($('#select_lower_mouth_child:checked').length == 0) {
        childlowkey = localStorage.getItem('childlowerkeys');
        image4.mapster('set', false, childlowkey);
    }
    getKeySelectedArray = Object.values(checkedValues);
    _.each(getKeySelectedArray, function(sol) {
        if (sol == 'uppermouth') {
            upkey = localStorage.getItem('upperkeys');
            console.log('..........upperkeyset.....',upkey)
            image1.mapster('set', true, upkey);
        }
        if (sol == 'uppermouth_child') {
            childupkey = localStorage.getItem('childupperkeys');
            console.log('..........childupperkeyset.....',childupkey)
            image3.mapster('set', true, childupkey);
        }
        if (sol == 'lowermouth'){
            lowkey = localStorage.getItem('lowerkeys');
            console.log('..........upperkeyset.....',lowkey)
            image2.mapster('set', true, lowkey);
        }
        if (sol == 'lowermouth_child'){
            childlowkey = localStorage.getItem('childlowerkeys');
            console.log('..........childupperkeyset.....',childlowkey)
            image4.mapster('set', true, childlowkey);
        }
    });
});


var image1 = $('#UT');
var image2 = $('#LT');
var image3 = $('#childUT');
var image4 =$('#childLT');
default_options = {
    fillOpacity: 0.5,
    render_highlight: {
        fillColor: '2aff00',
        stroke: true,
    },
    render_select: {
        fillColor: 'ff000c',
        stroke: false,
    },
    fadeInterval: 50,
    isSelectable: true,
    mapKey: 'data-key',

    onConfigured:  function() {
        var csv = '';
        var toothkey = localStorage.getItem('test') || "";
        
        upkey = localStorage.getItem('upperkeys');
        lowkey = localStorage.getItem('lowerkeys');
        childupkey = localStorage.getItem('childupperkeys');
        childlowkey = localStorage.getItem('childlowerkeys');
        var temp = toothkey.split(","), val, new_val, toothkey2 = "";
        for (var t=0;t<temp.length;t++) {
            try {
                new_val = temp[t].split("_");
                val = new_val[1];
                if (new_val[0] == 'toothcap' && val && parseInt(val) < 10) {
                    temp[t] = new_val[0] + "_" + parseInt(val);
                }
            }
            catch (err) {}
            toothkey2 += temp[t] + ",";
        }
        if (toothkey2) {
            toothkey2 = toothkey2.slice(0, -1);
        }
        csv = toothkey2 ? csv + toothkey2 : csv;
        csv = upkey ? csv + upkey : csv;
        csv = lowkey ? csv + lowkey : csv;
        csv = childupkey ? csv + childupkey : csv;
        csv = childlowkey ? csv + childlowkey : csv;

        var setChk = (toothkey2||upkey||lowkey);
        if(setChk){
            $('input:checkbox[name=mouthselection]').each(function(event) {
                if($(this).is(':checked')) {
                    var selected_chkbox =($(this).val());
                    if (selected_chkbox == 'uppermouth') {
                        image1.mapster('set', true, csv);
                    }
                    if (selected_chkbox == 'lowermouth') {
                        image2.mapster('set', true, csv);
                    }
                    if (selected_chkbox == 'uppermouth_child') {
                        image3.mapster('set', true, csv);
                    }
                    if (selected_chkbox == 'lowermouth_child') {
                        image4.mapster('set', true, csv);
                    }
                }
            });
        }
    }
};
$.mapster.impl.init();
$('#UT, #LT, #childUT, #childLT').mapster(default_options);

$('#toothmapupper area, #lowermoutharea area, #child_uppermouth area, #child_lowermouth area').each(function() {
    $(this).mouseover(function() {
        var found = false;
        var description = ""
        var surface = $(this).attr('id');
        $('#progres_table tr').each(function() {
            $(this).children().each(function() {
                var table_surface = $(this).text().replace(" ", "").split(",")
                for (var i = 0; i < table_surface.length; i++) {
                    if (surface == table_surface[i]) {
                        found = true;
                        description = $(this).parent().find("td[id*='desc']").text()
                    }
                }
            });
        });
        if (found) {
            this.title = description
        }
    });
});


$('[data-toggle="tooltip"]').tooltip();

});

//$('#toothmapupper area, #lowermoutharea area, #child_uppermouth area, #child_lowermouth area').each(function() {
//    $(this).click(function(e) {
//    	e.preventDefault();
//    	var image_as = $('#UT');
//    	console.log("______________on click ____________________",this)
//    	console.log("***********************************2",$(this).attr('data-key'),$(this).attr('title'))
//    	console.log("\n data title^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",$(this).attr('data-original-title title'));
//        if ($(this).attr('title')){
//        	console.log("___Already selected______________foundddddddddddddd",$(this).attr('data-key'));
//        	var area_array=[]
//        	area_array.push($(this).attr('data-key'))
//        	console.log("Area array as=++++++++++++++++++++++++",area_array.join())
//        	
//        	
////        	image_as.mapster({
//////				    set:true,
////					areas: area_array.join(),
////				    fillColor:'00ffff'
////				   
////				});
//        	
//        	var imagss_as=image_as.mapster({set: true, arear:area_array.join(), fillColor: '00ffff'});
//        	
//        	var imagres_as=$(this).mapster('set', true, area_array.join(), {fillColor: '00ffff'});
//        	console.log("******************11******************ENDDDDDDDD")
////        	return false;
//        }
//        return false;
//    });

//});
