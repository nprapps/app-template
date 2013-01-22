$(function() {
    // Constants for the live chat/widget
    var CHAT_ID = '74796';
    var CHAT_TOKEN = 'FtP7wRfX';
    var CHAT_UPDATE_INTERVAL = 5000;

    // Caching some DOM objects
    var $live = $('#live-chat');

    $live.livechat({
        chat_id: CHAT_ID,
        chat_token: CHAT_TOKEN,
        update_interval: CHAT_UPDATE_INTERVAL,
        alert_interval: 500,
        read_only: false
    });
});
