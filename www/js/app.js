// Global jQuery references
var $shareModal = null;
var $commentCount = null;

// Global state
var firstShareLoad = true;

/*
 * Run on page load.
 */
var onDocumentLoad = function(e) {
    // Cache jQuery references
    $shareModal = $('#share-modal');
    $commentCount = $('.comment-count');

    // Bind events
    $shareModal.on('shown.bs.modal', onShareModalShown);
    $shareModal.on('hidden.bs.modal', onShareModalHidden);

    // configure ZeroClipboard on share panel
    ZeroClipboard.config({ swfPath: 'js/lib/ZeroClipboard.swf' });
    var clippy = new ZeroClipboard($(".clippy"));

    clippy.on('ready', function(readyEvent) {
        clippy.on('aftercopy', onClippyCopy);
    });

    renderExampleTemplate();
    getCommentCount(showCommentCount);
}

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

/*
 * Share modal opened.
 */
var onShareModalShown = function(e) {
    ANALYTICS.openShareDiscuss();

    if (firstShareLoad) {
        loadComments();

        firstShareLoad = false;
    }
}

/*
 * Share modal closed.
 */
var onShareModalHidden = function(e) {
    ANALYTICS.closeShareDiscuss();
}

/*
 * Text copied to clipboard.
 */
var onClippyCopy = function(e) {
    alert('Copied to your clipboard!');

    ANALYTICS.copySummary();
}

$(onDocumentLoad);
