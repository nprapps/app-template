/*
 * Configure our ad slots and targeting.
 */
function setup_ads() {
    // Desktop ad slot
    if (DFP.shouldRenderForDevice('desktop')) {
        googletag.defineSlot('/6735/n6735.' + APP_CONFIG.NPR_DFP.ENVIRONMENT + '/' + APP_CONFIG.NPR_DFP.TARGET, [[300,250]], 'ad-desktop').addService(googletag.pubads());
    }

    // Mobile ad slot
    if (DFP.shouldRenderForDevice('88')) {
        googletag.defineSlot('/6735/n6735.' + APP_CONFIG.NPR_DFP.ENVIRONMENT + '/' + APP_CONFIG.NPR_DFP.TARGET, [88,31], 'ad-88').addService(googletag.pubads());
    }

    // Story targeting
    googletag.pubads().setTargeting('storyId', APP_CONFIG.NPR_DFP.STORY_ID);
    googletag.pubads().setTargeting('testserver', APP_CONFIG.NPR_DFP.TESTSERVER);

    // Device
    var ua = navigator.userAgent.toLowerCase();

    if (ua.indexOf('android') > -1) {
        googletag.pubads().setTargeting('device', 'android');
    } else if (ua.match(/(iPad|iPhone|iPod)/i)) {
        googletag.pubads().setTargeting('device', 'ios');
    }

    // ????
    if (typeof DFP.queryParameters.sc === 'string' && DFP.queryParameters.sc.length > 0) {
        scValue = DFP.queryParameters.sc;
    } else if (typeof document.referrer === 'string' && document.referrer.search('facebook.com') > -1) {
        scValue = 'fb';
    } else if (typeof DFP.queryParameters.ft === 'string') {
        scValue = DFP.queryParameters.ft;
    }
    
    googletag.pubads().setTargeting('sc', scValue);

    // Timezones
    var utm_source = typeof DFP.queryParameters.utm_source === 'string' && DFP.queryParameters.utm_source.length > 0?DFP.queryParameters.utm_source:'';
    var utm_medium = typeof DFP.queryParameters.utm_medium === 'string' && DFP.queryParameters.utm_medium.length > 0?DFP.queryParameters.utm_medium:'';

    googletag.pubads().setTargeting('utm_source', utm_source);
    googletag.pubads().setTargeting('utm_medium', utm_medium);

    // Orientation
    var orient = '';

    if (NPR.Devices.isOnPhone() || NPR.Devices.isOnTablet()) {
        if (window.orientation == 0 || window.orientation == 180) {
            orient = 'portrait';
        } else if (window.orientation == 90 || window.orientation == -90) {
            orient = 'landscape';
        }
    }
    
    googletag.pubads().setTargeting('orient', orient);

    googletag.pubads().enableSingleRequest();
    googletag.pubads().collapseEmptyDivs();
    googletag.enableServices();
}

/* 
 * Execute configuration when Google is ready.
 */
googletag.cmd.push(function() {
    try {
        setup_ads();
    } catch(e) {
        NPR.messaging.exception(e, 'Define Google Publisher Tags', NPR.messaging.constants.SPONSORSHIP_ERROR);
    }
});

