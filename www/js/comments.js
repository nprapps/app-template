var EVENT_CATEGORY = APP_CONFIG.PROJECT_SLUG;


var $comments = null;
var $commentButton = null;
var $commentCount = null;
var fullpage = false;
var disqusEndpoint = "https://disqus.com/api/3.0/threads/details.jsonp?api_key=tIbSzEhGBE9NIptbnQWn4wy1gZ546CsQ2IHHtxJiYAceyyPoAkDkVnQfCifmCaQW&thread%3Aident="
var commentCount = null;

var renderCommentCount = function(data) {
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

var onCommentButtonClick = function() {
    if ( $comments.hasClass('show') ) {
        $comments.removeClass('show');
    } else {
        $comments.addClass('show');
    }

    _gaq.push(['_trackEvent', EVENT_CATEGORY, 'Clicked to reveal comments']);

    return false;
}

$(function() {
    $comments = $('#comments');
    $commentButton = $('.comment-button');
    $commentCount = $('.comment-count');
    fullpage = $comments.hasClass('fullpage');

    var context = $.extend(APP_CONFIG, {});
    var html = JST.comments();

    $comments.html(html);

    $commentButton.on('click', onCommentButtonClick);

    $.ajax({
        url: disqusEndpoint + APP_CONFIG.DISQUS_SHORTNAME + "-comments&forum=" + APP_CONFIG.DISQUS_SHORTNAME,
        dataType: "jsonp",
        success: renderCommentCount
    });
});

