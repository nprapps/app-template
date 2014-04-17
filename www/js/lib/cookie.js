(function($){
    AddNamespace('NPR.util');
    var __filename = 'cookie.js';
    var at = undefined,
        _methods = {
            init: function() {
                var _at, p, q, x;
                if(typeof at === 'undefined') {
                    try{
                        _at = get_cookie('at');
                        if(typeof _at !== 'undefined' && _at !== null) {
                            at = {};
                            p = _at.split('&');
                            for(x in p) {
                                q = p[x].split('=');
                                if(q.length > 2) {
                                    // Might want to log a debug message here
                                } else if(q.length === 2) {
                                    // Hack because email should not convert + symbol to a space
                                    if(q[0] == 'e') {
                                        at[q[0]] = decodeURIComponent(q[1]);
                                    } else {
                                        at[q[0]] = decodeURIComponent(q[1].replace(/\+/g," "));
                                    }
                                }
                            }
                        } else {
                            at = undefined;
                        }
                    } catch(e) {
                        NPR.messaging.exception(e, __filename,'cookie.init', NPR.messaging.constants.EVENT_JS_ERROR);
                    }
                }
            }
        },
        methods = {
            /**
             * Specifically for use with the NPR at cookie
             * could extend this to get any cookie in the future
             */
            cookie: {
                getKey: function(key){
                    if(methods.cookie.exists(key)) {
                        return at[key];
                    }
                },
                exists: function(key) {
                    _methods.init();
                    if(typeof at !== 'undefined' && key in at) {
                        return true;
                    }
                    return false;
                },
                full: function() {
                    _methods.init();
                    return at;
                },
                reset: function(callback) {
                    at = undefined;
                    _methods.init();
                    callback();
                }
            }
        }
    $.extend(true, NPR.util, methods);

    $.cookie = function(name, value, options){
        if (typeof value != 'undefined') { // name and value given, set cookie
            options = options || {};
            if (value === null) {
                value = '';
                options.expires = -1;
            }
            var expires = '';
            if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) {
                var date;
                if (typeof options.expires == 'number') {
                    date = new Date();
                    date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
                } else {
                    date = options.expires;
                }
                expires = '; expires=' + date.toUTCString(); // use expires attribute, max-age is not supported by IE
            }
            // CAUTION: Needed to parenthesize options.path and options.domain
            // in the following expressions, otherwise they evaluate to undefined
            // in the packed version for some reason...
            var path = options.path ? '; path=' + (options.path) : '';
            var domain = options.domain ? '; domain=' + (options.domain) : '';
            var secure = options.secure ? '; secure' : '';
            document.cookie =[name,'=',encodeURIComponent(value),expires,path,domain,secure] .join('');
        } else { // only name given, get cookie
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = $.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    };

    $.removeCookie = function (key, options) {
        if ($.cookie(key) !== undefined) {
            // Must not alter options, thus extending a fresh object...
            $.cookie(key, '', $.extend({}, options, { expires: -1 }));
            return true;
        }
        return false;
    };

    /**
     * Returns a ready to use newsletter id array.
     */
    $.newsletterscookie = function() {
        var cookie = $.cookie('nl');
        if (cookie === null) {
            return null;
        }
        return cookie.split(",");
    };

    /**
     * Returns a ready to use station array.
     */
    $.stationscookie = function() {
        var cookie = $.cookie('st');
        if (cookie === null) {
            return null;
        }
        return cookie.split(",");
    };

    /**
     * Returns a ready to use Javascript object.
     */
    $.authcookie = function() {

        var obj = {};
        var cookie = $.cookie('at');
        if (cookie === null) { return obj; }
        var items = cookie.split('&');
        for(var i = 0; i < items.length; i++) {
            var kv = items[i].split('=');
            var key = kv[0];
            var val = kv[1];
            switch (key) {
                case 'u':
                    obj.userid = val;
                    break;
                case 'a':
                    obj.username = val;
                    break;
                case 'e':
                    obj.email = val;
                    break;
                case 'f':
                    obj.fname = val;
                    break;
                case 'l':
                    obj.lname = val;
                    break;
                case 'g':
                    obj.gender = val;
                    break;
                default:
                    obj[key] = val;
            }
        }

        /*
         * Create a fullname field for convenience.
         * Do not create it if no valid values are found.
         */
        if (obj.fname !== 'undefined') {
            obj.fullname = obj.fname;
        }
        if (obj.lname !== 'undefined') {
            if (obj.fullname) {
                obj.fullname += ' ' + obj.lname;
            } else {
                obj.fullname = obj.lname;
            }
        }

        return obj;
    };
})(jQuery);