var $comments = null;
var $showComments = null;
var $hideComments = null;
var fullpage = false;

var onShowCommentsClick = function() {
    $comments.addClass('show');

    return false;
}

var onHideCommentsClick = function() {
    $comments.removeClass('show');

    return false;
}

$(function() {
    $comments = $('#comments');
    $showComments = $('.show-comments');
    $hideComments = $('.hide-comments');
    fullpage = $comments.hasClass('fullpage');

    var context = $.extend(APP_CONFIG, {});
    var html = JST.comments();

    $comments.html(html);

    console.log($showComments);

    $showComments.on('click', onShowCommentsClick);
    $hideComments.on('click', onHideCommentsClick);
});
