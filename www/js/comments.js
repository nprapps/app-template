var EVENT_CATEGORY = APP_CONFIG.PROJECT_SLUG;


var $comments = null;
var $commentButton = null;
var $commentCount = null;
var fullpage = false;
var disqusEndpoint = "https://disqus.com/api/3.0/threads/details.jsonp?api_key=tIbSzEhGBE9NIptbnQWn4wy1gZ546CsQ2IHHtxJiYAceyyPoAkDkVnQfCifmCaQW&thread%3Aident="
var commentCount = null;
var at = undefined;
var disqus_data;
var disqus_config;
var disqus_shortname;
var disqus_identifier;

var commentAuth = {
    /*
    * A series of methods for getting, parsing, and updating the auth cookie from NPR/Disqus.
    */
    init: function() {
        /*
        * Gets the correct bits from our cookie and serializes them to key/value pairs.
        */
        if (typeof at === 'undefined') {
            try {
                _at = commentAuth.getCookie('at');
                if (typeof _at !== 'undefined' && _at !== null) {
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
                console.log(e);
            }
        }
    },
    getCookie: function(key) {
        /*
        * Grabs the appropriate cookie based on a key.
        * Returns the results trimmed and URL-decoded.
        */
        var allCookies = document.cookie.split(';');
        for (var i=0;i<allCookies.length;i++) {
            if ($.trim(allCookies[i].split('=')[0]) == 'at') {
                return decodeURIComponent($.trim(allCookies[i].split('=')[1]));
            }
        }
    },
    getDisqusData: function() {
        /*
        * Sets global Disqus auth variables based on the auth cookie.
        */
        disqus_data = {}
        disqus_data.userId = commentAuth.getKey('u');
        disqus_data.hmac = commentAuth.getKey('dh');
        disqus_data.message = commentAuth.getKey('dm');
        disqus_data.timestamp = commentAuth.getKey('dt');
    },
    loadDisqusFrame: function(){
        commentAuth.getDisqusData();
        commentAuth.setDisqusConfig();

        console.log(disqus_data);
        /*
        * The next lines of code are supplied by DISQUS for rendering their iframe (widget).
        * They suggest that we do not modify the code below here.
        * Seriously. Hands (and feet) off.
        */
        var dsq=document.createElement('script');dsq.type='text/javascript';dsq.async=true;dsq.src='//'+disqus_shortname+'.disqus.com/embed.js';(document.getElementsByTagName('head')[0]||document.getElementsByTagName('body')[0]).appendChild(dsq);
    },

    setDisqusConfig : function() {
         if (typeof disqus_data.timestamp !== 'undefined') {
             $('#login-overlay-link').hide();

             disqus_config = function () {
                 this.page.remote_auth_s3 = disqus_data.message + ' ' + disqus_data.hmac + ' ' + disqus_data.timestamp;
                 this.page.api_key = 'K5ANvxVxS7meX7au7vJpUpqIgFqQcDBEH8q39Z8N750SFmBhaOLTsShueMWid956';
                 console.log(this.page);
             }
         }
     },

    /*
    * These are methods pried directly from NPR's comments auth and cookie libs.
    * Don't modify these without a doctor's note.
    */
    getKey: function(key){if(commentAuth.exists(key)){return at[key];}},
    exists: function(key){commentAuth.init();if(typeof at !=='undefined'&&key in at){return true;}return false;}
}

var onCommentButtonClick = function() {
    if ( $comments.hasClass('show') ) {
        $comments.removeClass('show');
    } else {
        $comments.addClass('show');
        _gaq.push(['_trackEvent', EVENT_CATEGORY, 'Clicked to reveal comments']);
    }

    commentAuth.loadDisqusFrame();

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

    if (!fullpage){ $comments.find('.comments-close').on('click', onCommentButtonClick); }

    loadCommentCount();
});

