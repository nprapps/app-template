AddNamespace('NPR.disqus');

var disqus_shortname, disqus_identifier, disqus_url, disqus_config;

(function($){

    var _methods = {
        init : function() {
            var disqusData = _methods.getDisqusData();

            // See if we've got an old timestamp, and try to renew if so
            if (typeof disqusData.timestamp !== 'undefined') {

                var expiration = 3600; // secs, 1 hour

                var ts  = new Date(disqusData.timestamp*1000);
                var now = new Date();

                var diff = Math.ceil((now - ts) / 1000); // to seconds

                if (diff > expiration) {
                    methods.reset(methods.renderIframe);
                    return;
                }
            }

            methods.renderIframe();
        },
        /**
         * Pulls the disqusData items off the cookie
         * @return {Object}
         */
        getDisqusData : function() {
            var disqusData = {};

            disqusData.userId = NPR.util.cookie.getKey('u');
            disqusData.hmac = NPR.util.cookie.getKey('dh');
            disqusData.message = NPR.util.cookie.getKey('dm');
            disqusData.timestamp = NPR.util.cookie.getKey('dt');

            return disqusData;
        },
        /**
         * Sets the global disqus_config variable used by disqus to load the iframe
         */
        setDisqusConfig : function() {
            var disqusData = _methods.getDisqusData();
            // User logged in check
            if (typeof disqusData.timestamp !== 'undefined') {
                $('#login-overlay-link').hide();

                disqus_config = function () {
                    this.page.remote_auth_s3 = disqusData.message + ' ' + disqusData.hmac + ' ' + disqusData.timestamp;
                    this.page.api_key = 'K5ANvxVxS7meX7au7vJpUpqIgFqQcDBEH8q39Z8N750SFmBhaOLTsShueMWid956';
                    this.callback.onNewComment = [function() { NPR.metrics.newComment(); }];
                }
            }
        },
        setDisqusGlobals : function() {
            disqus_shortname  = $('#disqus-npr').data('shortname');
            disqus_identifier = $('#disqus-npr').data('identifier');
            disqus_url        = $('#disqus-npr').data('url');
            disqus_title      = $('#disqus-npr').data('title');
        }
    },
    /**
     * Public methods exposed via NPR.disqus
     */
    methods = {
        renderIframe : function() {
            var lt_ie9 = $('html').hasClass('lt-ie9');

            var lte_medium_touch = (NPR.Devices.isScreenSmallerOrEqual(NPR.BREAKPOINT.MEDIUM) && Modernizr.touch);

            var lt_medium_with_ad_notouch = (NPR.Devices.isScreenSmaller(NPR.BREAKPOINT.MEDIUM_WITH_AD) && !Modernizr.touch);

            if (typeof NPR.responsivePage !== 'undefined') {
                if (NPR.responsivePage.renderMobileDisqus === false && (lt_ie9 || lte_medium_touch || lt_medium_with_ad_notouch)) {

                    return;
                }
                else {
                    NPR.responsivePage.registerCommentsActive();
                    NPR.responsivePage.renderMobileDisqus = true;
                }
            }

            _methods.setDisqusGlobals();
            _methods.setDisqusConfig();

            if ($('#disqus-npr').length) {
                /*
                 * The next lines of code are supplied by DISQUS for rendering their iframe (widget).
                 * They suggest that we do not modify the code below here
                 */
                var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
                dsq.src = 'http://' + disqus_shortname + '.disqus.com/embed.js';
                (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
            }
        },
        reload : function() {
            _methods.setDisqusConfig();
            if(typeof DISQUS !== 'undefined') {
                DISQUS.reset({
                    reload: true,
                    config: disqus_config
                })
            }
        },
        reset: function(callback) {
          $.get('/templates/community/renewCookie.php', {t: (new Date()).getTime()}, function(d){
            callback();
          });
        }
    };
    $.extend(true, NPR.disqus, methods);
    $(document).ready(_methods.init);
})(jQuery);