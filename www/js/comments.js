var EVENT_CATEGORY = APP_CONFIG.PROJECT_SLUG;


var $comments = null;
var $commentButton = null;
var $commentCount = null;
var fullpage = false;
var disqusEndpoint = "https://disqus.com/api/3.0/threads/details.jsonp?api_key=tIbSzEhGBE9NIptbnQWn4wy1gZ546CsQ2IHHtxJiYAceyyPoAkDkVnQfCifmCaQW&thread%3Aident="
var commentCount = null;
var disqus_config;
var disqus_shortname;
var disqus_identifier;

var getAuthCookie = function() {
    /*
    * Grabs the auth cookie.
    * Returns the results trimmed and URL-decoded.
    */
    var allCookies = document.cookie.split(';');

    for (var i = 0; i < allCookies.length; i++) {
        if ($.trim(allCookies[i].split('=')[0]) == 'at') {
            return decodeURIComponent($.trim(allCookies[i].split('=')[1]));
        }
    }

    return null;
}

var parseAuthCookie = function() {
    var cookie = getAuthCookie();

    if (!cookie) {
        return {};
    }

    var data = cookie.split('&');
    var parsed = {};

    for (pair in data) {
        var bits = data[pair].split('=');
        var key = bits[0];
        var val = bits[1];

        if (key != 'email') {
            val = val.replace(/\+/g, " ");
        }

        parsed[key] = decodeURIComponent(val);
    }

    return parsed;
}

var loadDisqusFrame = function() {
    var auth = parseAuthCookie();

    if (typeof auth['dt'] !== 'undefined') {
        $('#login-overlay-link').hide();

        disqus_config = function () {
            this.page.remote_auth_s3 = auth['dm'] + ' ' + auth['dh'] + ' ' + auth['dt'];
            this.page.api_key = 'K5ANvxVxS7meX7au7vJpUpqIgFqQcDBEH8q39Z8N750SFmBhaOLTsShueMWid956';
        }
    }

    /*
    * The next lines of code are supplied by DISQUS for rendering their iframe (widget).
    * They suggest that we do not modify the code below here.
    * Seriously. Hands (and feet) off.
    */
    var dsq=document.createElement('script');dsq.type='text/javascript';dsq.async=true;dsq.src='//'+disqus_shortname+'.disqus.com/embed.js';(document.getElementsByTagName('head')[0]||document.getElementsByTagName('body')[0]).appendChild(dsq);
}

var onCommentButtonClick = function() {
    if ( $comments.hasClass('show') ) {
        $comments.removeClass('show');
    } else {
        $comments.addClass('show');
        _gaq.push(['_trackEvent', EVENT_CATEGORY, 'Clicked to reveal comments']);
    }

    loadDisqusFrame();

    return false;
}

var renderCommentCount = function(data) {
    /*
    * Renders the comment count.
    */
    var thread = data.response;
    commentCount = thread.posts;

    $commentCount.text(commentCount);

    if (commentCount > 0) {
        $commentCount.addClass('has-comments');
    }

    if ( commentCount > 1) {
        $commentCount.next('.comment-label').text('Comments');
    }
}

var loadCommentCount = function() {
    /*
    * Loads the comment count from Disqus.
    * Calls renderCommentCount as a callback on success.
    */
    $.ajax({
        url: disqusEndpoint + disqus_shortname + "-comments&forum=" + disqus_shortname,
        dataType: "jsonp",
        success: renderCommentCount
    });
}

$(function() {
    $comments = $('#comments');
    $commentButton = $('.comment-button');
    $commentCount = $('.comment-count');

    fullpage = $comments.hasClass('fullpage');
    disqus_shortname = APP_CONFIG.DISQUS_SHORTNAME;
    disqus_identifier = disqus_shortname + '-comments';

    var context = $.extend(APP_CONFIG, {});
    var html = JST.comments();

    $comments.html(html);

    $commentButton.on('click', onCommentButtonClick);

    if (!fullpage) {
        $comments.find('.comments-close').on('click', onCommentButtonClick);
    }

    loadCommentCount();
});

