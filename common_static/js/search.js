'Use Strict';

var __IDS_Search;
;(function() {
    var _this = '';

    var _main_search_form = $('#search_form');


    var _location_array = [];
    var _advance_params = ['frequency', 'layout', 'venue', 'amenities', 'people'];

    __IDS_Search =
    {
        init: function()
        {
            _this = this;
            $('.temp-height-class').removeClass('temp-height-class');
            _main_search_form.find('select').each(function(){
                $(this).select2({
                    placeholder: $(this).attr('placeholder')
                });
            });
            _main_search_form.find('#id_location').select2({
                placeholder: $('#id_location').attr('placeholder'),
                minimumInputLength: 2
            });

            _main_search_form.find('.search_button').click(function() {
                $(this).html('<i class="fa fa-spinner fa-spin"></i>');
                _this._build_search_url(true, 0);
            });

            $('button.btn-filter').click(function() {
                _this._build_search_url(false, 0);
            });

            $('.location_filter, #id_sort_order').change(function() {
                _this._build_search_url(false, 0);
            });

            $('#id_price_min, #id_price_max').keypress(function (e) {
                if (e.which == 13) {
                    $('button.btn-filter').click();
                }
            });

            if($('#search').length) { // If search results page
                if(_this._check_if_advance())
                    $('.search-form-container .advance').click();
            }

            $('#search_listings .page-link').click(function(e) {
                e.preventDefault();
                _this._build_search_url(false, $(this).data('page'));
            });

            $('.search-form-container #id_location').select2({
                placeholder: $('.search-form-container #id_location').attr('placeholder'),
                minimumInputLength: 2,
                escapeMarkup: function (markup) { return markup; },
                templateResult: function (result) {
                    return result.htmlmatch ? result.htmlmatch : result.text;
                },
                matcher:function(params, data) {
                    if ($.trim(params.term) === '') {
                      return data;
                    }
                    if (typeof data.text === 'undefined') {
                      return null;
                    }

                    var idx = data.text.toLowerCase().indexOf(params.term.toLowerCase());
                    if (idx > -1) {
                      var modifiedData = $.extend({
                          'htmlmatch': data.text.replace(new RegExp( "(" + params.term + ")","gi") ,"<strong>$1</strong>")
                      }, data, true);

                      return modifiedData;
                    }

                    return null;
                }
            });

            $('#search_listings .save-item').click(function(e) {
                e.preventDefault();

                var elem = $(this);
                elem.find('i').addClass('fa-spinner fa-spin');
                $.post('/account/favorites/ae/', {'listing_id': elem.data('listing-id')}, function(response){
                    if(response && response.status == 'success') {
                        if(response.msg == 'added') {
                            elem.addClass('active');
                        } else {
                            elem.removeClass('active');
                        }
                    } else if(response && response.status == 'error') {
                        if(response.msg == 'signin') {
                            window.location.href = '/account/login';
                        }
                    }
                    elem.find('i').removeClass('fa-spinner fa-spin');
                });
            });

            $('.mobile-filters-btn').click(function() {
                $('.property_search_form').addClass('mobile-filter');
                $('#tidio-chat').addClass('hide');
            });

            $('.close-panel').on('click', function() {
                $('.property_search_form').removeClass('mobile-filter');
                $('#tidio-chat').removeClass('hide');
            });
        },

        _build_search_url: function(search_form, page_number) {
            var category = $('#id_category').val();
            var location = $('#id_location').val();
            var layout = $('#id_layout').val();
            var venue = $('#id_venue').val();
            var amenities = $('#id_amenities').val();
            var people = $('#id_people').val();
            var frequency = $('#id_frequency').val();

            var location_filter = [];
            var search_url = '/s/';
            var params = [];

            if(category) {
                search_url += category + '/';
            }

            _location_array = [];

            if(search_form && location) {
                if(location.length == 1) {
                    _this._get_locations_tree(location[0]);

                    if(_location_array.length) {
                        search_url += _location_array.reverse().join('/');
                    }

                } else if(location.length > 1) {
                    $.each($('#id_location').val(), function() {
                        params.push('location=' + this);
                    });
                }
            }

            if(amenities) {
                $.each($('#id_amenities').val(), function() {
                    params.push('amenities=' + this);
                });
            }

            if(layout) params.push('layout=' + layout);
            if(venue) params.push('venue=' + venue);
            if(people) params.push('people=' + people);
            if(frequency) params.push('frequency=' + frequency);

            // if(filters_enabled) {
            //     var sort_order = $('#id_sort_order').val();

            //     if(sort_order && sort_order != 'r') params.push('sort_order=' + sort_order);
            // }

            if (params.length) search_url += '?' + params.join('&');

            window.location = search_url;
        },

        _get_locations_tree: function(location_id) {
            var location = locationsArray[location_id];
            _location_array.push(location.slug);

            if('parent' in location) {
                _this._get_locations_tree(location.parent);
            }
        },
        _check_if_advance: function() {
            var sPageURL = decodeURIComponent(window.location.search.substring(1)),
                sURLVariables = sPageURL.split('&'),
                sParameterName,
                i;

            for (i = 0; i < sURLVariables.length; i++) {
                sParameterName = sURLVariables[i].split('=');

                if ($.inArray(sParameterName[0], _advance_params) >= 0) {
                    return true;
                }
            }

            return false;
        }
    };

    $(function() {
        __IDS_Search.init();
    });
})();
