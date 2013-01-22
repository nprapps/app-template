var NPR_AUTH = (function() {
    var my = {};
    var auth_callback = null;

    function _init_janrain() {
        /*
         * Initalize jainrain global configuration and import.
         */
        function e() {
            janrain.ready = true;
        }

        if (typeof window.janrain !== "object") window.janrain = {};
        if (typeof window.janrain.settings !== "object") window.janrain.settings = {};

        janrain.settings = {};
        janrain.settings.tokenAction = "event";
        janrain.settings.custom = true;
        janrain.settings.tokenUrl = "http://login.npr.org/";
        janrain.settings.appUrl = "https://login.npr.org/";
        janrain.settings.type = "embed";
        janrain.settings.appId = "odgehpicdimjmbgoofdi";
        janrain.settings.providers = ["facebook", "google", "yahoo"];

        if (document.addEventListener) {
            document.addEventListener("DOMContentLoaded", e, false);
        } else {
            window.attachEvent("onload", e);
        }

        var t = document.createElement("script");
        t.type = "text/javascript";
        t.id = "janrainAuthWidget";
        
        if (document.location.protocol === "https:") {
            t.src = "https://rpxnow.com/js/lib/login.npr.org/engage.js";
        } else {
            t.src = "http://widget-cdn.rpxnow.com/js/lib/login.npr.org/engage.js";
        }

        var n = document.getElementsByTagName("script")[0];
        n.parentNode.insertBefore(t, n);

        // Must be in global namespace for Janrain magic :-(
        window.janrainWidgetOnload = function() {
            janrain.events.onProviderLoginToken.addHandler(function(response) {
                $.ajax({
                    type: 'POST',
                    url: 'https://api.npr.org/infinite/v1.0/janrain/',
                    dataType: 'json',
                    data: { token: response.token, temp_user: null },
                    success: function(response){
                        if (response.status === 'success') {
                            auth_callback(response);
                        }
                    }
                });
            });
        }
    }

    my.login = function(service, callback) {
        /*
         * Login to an oauth service with janrain.
         */
        auth_callback = callback;
        janrain.engage.signin.triggerFlow(service);
    }

    _init_janrain();

    return my;
}());
