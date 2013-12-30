$(function() {
    // Constants for the live chat/widget
    // Caching some DOM objects
    var $live = $('#live-chat');

    // No box ad when we have adhesion, so #main-content gets 12 columns
    if (window.innerWidth <= 1024){
        $('#main-content').removeClass('col-md-8').addClass('col-md-12');
    }

    // Templating example
    var context = $.extend(APP_CONFIG, {
        'template_path': 'jst/example.html',
        'config': JSON.stringify(APP_CONFIG, null, 4),
        'copy': JSON.stringify(COPY, null, 4)
    });

    var html = JST.example(context);

    $('#template-example').html(html);
    $live.livechat({
        chat_id: APP_CONFIG['CHAT']['ID'],
        chat_token: APP_CONFIG['CHAT']['TOKEN'],
        update_interval: APP_CONFIG['CHAT']['UPDATE_INTERVAL'],
        alert_interval: 500,
        read_only: false
    });
});
