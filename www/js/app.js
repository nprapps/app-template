// Global jQuery references
var $commentCount = null;

/*
 * Run on page load.
 */
var onDocumentLoad = function(e) {
    // Cache jQuery references
    $commentCount = $('.comment-count');

    renderExampleTemplate();
    getCommentCount(showCommentCount);

    SHARE.setup();
    // testStorage();
}
/*
var testStorage = function() {
    var test = STORAGE.get('test');
    if (test) {
        STORAGE.deleteKey('test');
    }
    console.log(simpleStorage.index());
    console.log(STORAGE.get('test')); //nothing
    STORAGE.set('test', 'haha');
    console.log(STORAGE.get('test'), STORAGE.getTTL('test')); //haha
    STORAGE.setTTL('test', 1000);
    console.log(STORAGE.getTTL('test'));

    console.log(simpleStorage.index());
}
*/

/*
 * Basic templating example.
 */
var renderExampleTemplate = function() {
    var context = $.extend(APP_CONFIG, {
        'template_path': 'jst/example.html',
        'config': JSON.stringify(APP_CONFIG, null, 4),
        'copy': JSON.stringify(COPY, null, 4)
    });

    var html = JST.example(context);

    $('#template-example').html(html);
}

/*
 * Display the comment count.
 */
var showCommentCount = function(count) {
    $commentCount.text(count);

    if (count > 0) {
        $commentCount.addClass('has-comments');
    }

    if (count > 1) {
        $commentCount.next('.comment-label').text('Comments');
    }
}

$(onDocumentLoad);
