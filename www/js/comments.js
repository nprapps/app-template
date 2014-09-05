var disqusEndpoint = "https://disqus.com/api/3.0/threads/details.jsonp?api_key=" + APP_CONFIG.DISQUS_API_KEY + "&thread%3Aident="
var disqus_config;
var disqus_shortname;
var disqus_identifier;

/*
 * Some configuration must be set on page load.
 */
var configureComments = function() {
    disqus_shortname = APP_CONFIG.DISQUS_SHORTNAME;
    disqus_identifier = APP_CONFIG.PROJECT_SLUG + '-' + APP_CONFIG.DISQUS_UUID;
}

/*
 * Writes the Disqus frame and sets some configuration.
 */
var loadComments = function() {
    // Get the auth bits from the cookie.
    var auth = parseAuthCookie();

    // If we've got our auth bits, set up a callback function.
    if (typeof auth['dt'] !== 'undefined') {

        // Hide the login bits.
        $('#login-overlay-link').hide();
        $('#logout-overlay-link').show();

        // Set up a callback function to use later. Apparently.
        disqus_config = function () {
            this.page.remote_auth_s3 = auth['dm'] + ' ' + auth['dh'] + ' ' + auth['dt'];
            this.page.api_key = 'K5ANvxVxS7meX7au7vJpUpqIgFqQcDBEH8q39Z8N750SFmBhaOLTsShueMWid956';

            this.callbacks.onNewComment = [
                function() {
                    _gaq.push(['_trackEvent', APP_CONFIG.PROJECT_SLUG, 'new-comment']);
                    trackComment();
                }
            ];
        }
    }

    /*
    * The next lines of code are supplied by DISQUS for rendering their iframe (widget).
    * They suggest that we do not modify the code below here.
    * Seriously. Hands (and feet) off.
    */
    var dsq=document.createElement('script');dsq.type='text/javascript';dsq.async=true;
    dsq.src='//'+disqus_shortname+'.disqus.com/embed.js';
    (document.getElementsByTagName('head')[0]||document.getElementsByTagName('body')[0]).appendChild(dsq);
}

/*
 * Loads the comment count from Disqus and calls a callback.
 */
var getCommentCount = function(callback) {
    $.ajax({
        url: disqusEndpoint + APP_CONFIG.PROJECT_SLUG + "-" + APP_CONFIG.DISQUS_UUID + "&forum=" + disqus_shortname,
        dataType: "jsonp",
        success: function(data) {
            callback(data.response.posts);
        }
    });
}

/*
 * Grabs the auth cookie.
 * Returns the results trimmed and URL-decoded.
 */
var getAuthCookie = function() {

    // Get all cookies this domain can see.
    var allCookies = document.cookie.split(';');

    // Get our cookie, 'at,' and return it trimmed and deurlified.
    for (var i = 0; i < allCookies.length; i++) {

        // Our cookie is called 'at'. For some reason.
        if ($.trim(allCookies[i].split('=')[0]) == 'at') {

            // Send it out!
            return decodeURIComponent($.trim(allCookies[i].split('=')[1]));
        }
    }

    return null;
}

/*
 * Parses the cookie out to an object.
 * Returns an object with the necessary auth components to renew a cookie.
 */
var parseAuthCookie = function() {
    var cookie = getAuthCookie();

    // If there's no cookie, return an empty object.
    if (!cookie) {
        return {};
    }

    // Our cookie data is a urlencoded string. So split on &'s.
    var data = cookie.split('&');
    var parsed = {};

    // Loop over the key/value pairs.
    for (pair in data) {

        // Split to keys and values.
        var bits = data[pair].split('=');
        var key = bits[0];
        var val = bits[1];

        // This is a great story. You should ask @onyxfish about it.
        if (key != 'email') {
            val = val.replace(/\+/g, " ");
        }

        // Decode the value, just in case.
        parsed[key] = decodeURIComponent(val);
    }

    return parsed;
}


$(configureComments);

