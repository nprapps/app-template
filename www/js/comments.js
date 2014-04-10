var renderComments = function() {
    var context = $.extend(APP_CONFIG, {});
    var html = JST.comments();

    $('#comments').html(html);
}
