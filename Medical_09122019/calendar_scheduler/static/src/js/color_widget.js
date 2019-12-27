odoo.define('calendar_scheduler.colorpicker', function(require) {
    "use strict";

    var field_registry = require('web.field_registry');
    var Field = field_registry.get('char');


    var FieldColorPicker = Field.extend({

        template: 'FieldColorPicker',
        widget_class: 'oe_form_field_color',
        cssLibs: [
            '/calendar_scheduler/static/lib/bootstrap-colorpicker/css/bootstrap-colorpicker.css'
        ],
        jsLibs: [
            '/calendar_scheduler/static/lib/bootstrap-colorpicker/js/bootstrap-colorpicker.js'
        ],

        _renderReadonly: function () {
            var show_value = this._formatValue(this.value);
            this.$el.text(show_value);
            this.$el.css("background-color", show_value);

        },

        _getValue: function () {
            var $input = this.$el.find('input');

            var val = $input.val();
            var isOk = /^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+(?:\.\d+)?))?\)$/i.test(val);

            if (!isOk) {
                    return 0;
                }

            return $input.val();


        },

        _renderEdit: function () {
                var show_value = this.value ;
                var $input = this.$el.find('input');
                $input.val(show_value);
                try{
                    this.$el.colorpicker({format: 'rgba'});
                    this.$input = $input;
                }
                catch(err){
                    alert("Please activate developer mode with assets for proper working.")
                }
        }

    });

    field_registry.add('colorpicker', FieldColorPicker);

	return {
	    FieldColorPicker: FieldColorPicker
	};
});
