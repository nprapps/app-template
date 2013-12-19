var ADS = {};
var googletag = { cmd: [] };

/*
 * Are we on a tablet?
 */
ADS.isOnTablet = function() {
    var width = window.innerWidth;

    return (width >= 768 && width <= 1024);
}

/*
 * Are we on a phone?
 */
ADS.isOnPhone = function() {
    var width = window.innerWidth;

    return width <= 767;
}

/*
 * Logic to determine if we should render a certain ad.
 */
ADS.shouldRenderForDevice = function(deviceEnv) {
    if (!deviceEnv) {
        return false;
    } else {
        var shouldRender = false;
        var winWidth = $(window).width();
        var winOrientation = window.orientation;

        switch (deviceEnv) {
            case 'desktop':
                var ieEightCheck = ($.browser.msie === true && ($.browser.version === '7.0' || $.browser.version === '8.0'));
                if (ieEightCheck) {
                    shouldRender = true;
                } else if (!ADS.isOnTablet() && winWidth > 1024) {
                    shouldRender = true;
                }
                
                break;
            case 'mobile':
                if ((ADS.isOnPhone() || ADS.isOnTablet()) && winWidth >= 300 && winWidth <= 1024) {
                    // block ads from ever showing on small-screen mobile devices
                    if (winWidth >= 480 || winOrientation == 0 || winOrientation == 180) {
                        shouldRender = true;
                    }
                }
                break;
            default:
                break;
        }
		//console.log(deviceEnv + ' shouldRender: ' + shouldRender);
        return shouldRender;
    }
}


/*
 * Configure our ad slots and targeting.
 */
ADS.setup_ads = function() {
    // Desktop ad slot
    if (ADS.shouldRenderForDevice('desktop')) {
        googletag.defineSlot('/6735/n6735.' + APP_CONFIG.NPR_DFP.ENVIRONMENT + '/' + APP_CONFIG.NPR_DFP.TARGET, [[300,250]], 'ad-desktop').addService(googletag.pubads());
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

    if (ADS.isOnPhone() || ADS.isOnTablet()) {
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

/* 
 * Execute configuration when Google is ready.
 */
googletag.cmd.push(function() {
    try {
        ADS.setup_ads();
    } catch(e) {
        NPR.messaging.exception(e, 'Define Google Publisher Tags', NPR.messaging.constants.SPONSORSHIP_ERROR);
    }
});

ADS.setup_googletag();
