var reloadTimestamp;

var RELOAD = (function() {
    var getTimestamp = function() {
        if (reloadTimestamp == null) {
            checkTimestamp();
        }
        setInterval(checkTimestamp, APP_CONFIG.RELOAD_CHECK_INTERVAL * 1000);
    }

    var checkTimestamp = function() {
        $.ajax({
            'url': 'live-data/timestamp.json',
            'cache': false,
            'success': function(data) {
                var newTime = data['timestamp'];

                if (reloadTimestamp == null) {
                    reloadTimestamp = newTime;
                }
                if (reloadTimestamp != newTime) {
                    window.location.reload(true);
                }
            },
        });
    }

    return {
        'getTimestamp': getTimestamp
    }
}());

$(document).ready(function() {
    RELOAD.getTimestamp();
});
