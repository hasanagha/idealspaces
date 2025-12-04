'Use Strict';

if (!$) {
    $ = django.jQuery;
}

var __AD;
;(function() {
    var _this = '';

    __AD =
    {
        init: function()
        {
            _this = this;

            // jQuery('textarea').tinymce({
            //   script_url : '/static/libs/tinymce/tinymce.min.js',
            //   // theme : "inlite",
            // });

            jQuery('#listing_form').on('change', '.field-asset_type select', function() {
                var type = 'file';
                var parent = jQuery(this).closest('tr');

                if(jQuery(this).val() == 'V') {
                    parent.find('.field-url .file-input').hide();
                    parent.find('.field-url .file-url').attr('type', 'text');
                } else {
                    parent.find('.field-url .file-input').show();
                    parent.find('.field-url .file-url').attr('type', 'hidden');
                }
            });

            if(jQuery('#assets-group').length) {
                _this._convertFieldTypeOnLoad();
            }
        },

        _convertFieldTypeOnLoad: function() {
            jQuery('.field-asset_type select').each(function() {
                if(jQuery(this).val() && jQuery(this).val() == 'V') {
                    var parent = jQuery(this).closest('tr');
                    parent.find('.field-url .file-input').hide();
                    parent.find('.field-url .file-url').attr('type', 'text');
                } 
            });
        }

    };

    jQuery(function() {
        __AD.init();
    });
})();
