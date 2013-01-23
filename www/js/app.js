$(function() {
    // Constants for the live chat/widget
    // Caching some DOM objects
    var $live = $('#live-chat');

    $live.livechat({
        chat_id: APP_CONFIG['CHAT']['ID'],
        chat_token: APP_CONFIG['CHAT']['TOKEN'],
        update_interval: APP_CONFIG['CHAT']['UPDATE_INTERVAL'],
        alert_interval: 500,
        read_only: false
    });
});
