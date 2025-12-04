;var Utils =
{
    ScreenSizes: {
        'mobile': 764,
        'tablet': 1023,
        'desktop': 1024,
    },
    General:{
        getUrlVars: function(){
            var obj = {};
            var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
            $.each(hashes, function(key, val){
                var hash = val.split('=');
                obj[hash[0]] = hash[1];
            });
            return obj;
        },
        getUrlAnchor: function(){
            var hash = location.hash.replace('#','');
            return hash;
        },
        getUrlPathname: function(){
            return window.location.pathname;
        },
        getUrlPathArray: function(){
            return window.location.pathname.split("/");
        },
        getUrlParamKeyValue: function(query){
            var query_string = {};
            var query = query?query:window.location.search.substring(1);
            var vars = query.split("&");
            for (var i=0;i<vars.length;i++) {
                var pair = vars[i].split("=");
                // If first entry with this name
                if (typeof query_string[pair[0]] === "undefined") {
                    query_string[pair[0]] = pair[1];
                // If second entry with this name
                } else if (typeof query_string[pair[0]] === "string") {
                    var arr = [ query_string[pair[0]], pair[1] ];
                    query_string[pair[0]] = arr;
                    // If third or later entry with this name
                } else {
                    query_string[pair[0]].push(pair[1]);
                }
            }
            return query_string;
        },
        getSpecificUrlPart: function(part, url) {
            var params = url?url:this.getUrlPathArray();

            if(typeof(params) == "string"){
                params = params.split("/");
            }

            var result = null;
            _.each(params, function(v){
                if(v.indexOf(part) == 0 )
                    result = v;
            })
            return result;
        },
        getDomainName: function() {
            var parts = location.hostname.split('.');
            var subdomain = parts.shift();
            var upperleveldomain = parts.join('.');
            return upperleveldomain;
        },
        getSiteDataAttributes: function(attribute){
            return $("html").data(attribute);
        },
        getNonProtocolHost: function(){
            return "//" + window.location.host;
        },
        getNonProtocolHostWithLang: function(){
            return "//" + window.location.host + "/" + this.getSiteDataAttributes("lang");
        }
    },
    Check:{
        isMobile: function(){
            var screenWidth = $(window).width();
            if(screenWidth <= Utils.ScreenSizes.mobile){
                return true;
            }
            return false;
        },
        isTablet: function(){
            var screenWidth = $(window).width();
            if(screenWidth > Utils.ScreenSizes.mobile && screenWidth <= Utils.ScreenSizes.tablet){
                return true;
            }
            return false;
        },
        isTabletLandscape: function(){
            var screenWidth = $(window).width();
            if(screenWidth > Utils.ScreenSizes.tablet && screenWidth <= Utils.ScreenSizes.desktop){
                return true;
            }
            return false;
        },
        isDesktop: function(){
            var screenWidth = $(window).width();
            if(screenWidth >= Utils.ScreenSizes.desktop){
                return true;
            }
            return false;
        },
        elemIsOnViewPort: function(_elem){
            if(_elem == undefined) return false;
            var partial         = true; //if true, will check the top of element in viewport else bottom of the elem
            var docViewTop      = $(window).scrollTop();
            var docViewBottom   = docViewTop + $(window).height();

            var elemTop         = $(_elem).offset().top;
            var elemBottom      = elemTop + $(_elem).height();

            var compareTop      = partial === true ? elemBottom : elemTop;
            var compareBottom   = partial === true ? elemTop : elemBottom;

            return ((compareBottom <= docViewBottom) && (compareTop >= docViewTop));
        },
        elemVisibility: function(obj) {
            var winw = jQuery(window).width(), winh = jQuery(window).height(),
                elw = obj.width(), elh = obj.height(),
                o = obj[0].getBoundingClientRect(),
                x1 = o.left - winw, x2 = o.left + elw,
                y1 = o.top - winh, y2 = o.top + elh;

            return [
                Math.max(0, Math.min((0 - x1) / (x2 - x1), 1)),
                Math.max(0, Math.min((0 - y1) / (y2 - y1), 1))
            ];
        }
    },
    Browser: {
        // Opera 8.0+
        isOpera: function() {
             return (!!window.opr && !!opr.addons) || !!window.opera || navigator.userAgent.indexOf(' OPR/') >= 0;   
        },

        // Firefox 1.0+
        isFirefox: function() {
             return typeof InstallTrigger !== 'undefined';   
        },

        // Safari 3.0+ "[object HTMLElementConstructor]" 
        isSafari: function() {
             return /constructor/i.test(window.HTMLElement) || (function (p) { return p.toString() === "[object SafariRemoteNotification]"; })(!window['safari'] || (typeof safari !== 'undefined' && safari.pushNotification));   
        },

        // Internet Explorer 6-11
        isIE: function() {
             return /*@cc_on!@*/false || !!document.documentMode;   
        },

        // Edge 20+
        isEdge: function() {
             return !isIE && !!window.StyleMedia;   
        },

        // Chrome 1+
        isChrome: function() {
             return !!window.chrome && !!window.chrome.webstore;   
        },

        // Blink engine detection
        isBlink: function() {
             return (isChrome || isOpera) && !!window.CSS;   
        }    
    }
}
