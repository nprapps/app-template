var ADS = {};
var googletag = { cmd: [] };

/*
 * Configure our ad slots and targeting.
 */
ADS.setup_ads = function() {
    // Desktop ad slot
    if (!Modernizr.touch && Modernizr.mq('(min-width: 1025px)')) {
        googletag.defineSlot('/6735/n6735.' + APP_CONFIG.NPR_DFP.ENVIRONMENT + '/' + APP_CONFIG.NPR_DFP.TARGET, [300,250], 'ad-desktop').addService(googletag.pubads());
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

    // Orientation
    var orient = '';

    if (Modernizr.touch && Modernizr.mq('(max-width: 1024px)')) {
        if (Modernizr.mq('(orientation: portrait)')) {
            orient = 'portrait';
        } else if (Modernizr.mq('(orientation: landscape)')) {
            orient = 'landscape';
        }
    }
    
    googletag.pubads().setTargeting('orient', orient);

    googletag.pubads().enableSingleRequest();
    googletag.pubads().collapseEmptyDivs();
    googletag.enableServices();
};

/*
 * Load Google JS.
 */
ADS.setup_googletag = function() {
    var gads = document.createElement('script');
    gads.async = true;
    gads.type = 'text/javascript';
    var useSSL = 'https:' == document.location.protocol;
    gads.src = (useSSL ? 'https:' : 'http:') + '//www.googletagservices.com/tag/js/gpt.js';
    var node = document.getElementsByTagName('script')[0];
    node.parentNode.insertBefore(gads, node);
};

// Configure when ready
googletag.cmd.push(function() {
    try {
        ADS.setup_ads();
    } catch(e) {
        NPR.messaging.exception(e, 'Define Google Publisher Tags', NPR.messaging.constants.SPONSORSHIP_ERROR);
    }
});

// Render desktop ad if needed
if (!Modernizr.touch && Modernizr.mq('(min-width: 1025px)')) {
    googletag.cmd.push(function() {
        googletag.display('ad-desktop');
    });
}

// Load Google
ADS.setup_googletag();
