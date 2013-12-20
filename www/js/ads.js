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
    var shouldRender = false;
    var winWidth = $(window).width();

    switch (deviceEnv) {
        case 'desktop':
            if (!ADS.isOnTablet() && winWidth > 1024) {
                shouldRender = true;
            }
            
            break;
        case 'mobile':
            if ((ADS.isOnPhone() || ADS.isOnTablet())) {
                shouldRender = true;
            }

            break;
    }

    //console.log('shouldRenderForDevice(' + deviceEnv + '): ' + shouldRender);

    return shouldRender;
}


/*
 * Configure our ad slots and targeting.
 */
ADS.setup_ads = function() {
    // Desktop ad slot
    if (ADS.shouldRenderForDevice('desktop')) {
        googletag.defineSlot('/6735/n6735.' + APP_CONFIG.NPR_DFP.ENVIRONMENT + '/' + APP_CONFIG.NPR_DFP.TARGET, [300,250], 'ad-desktop').addService(googletag.pubads());
    }

    // Adhesion ad slot
    // NB: Using ad slots for adhesion doesn't work for reasons that are unclear
    // The NPR.org homepage doesn't do it this way either
    /*if (ADS.shouldRenderForDevice('mobile')) {
        var size = [640, 100];

        //if (Modernizr.mq('only screen and (min-width: 768px)')) {
            size = [2048, 180];
        //}

        googletag.defineSlot('/6735/n6735.nprmobile/' + APP_CONFIG.NPR_DFP.TARGET, size, 'adhesion').addService(googletag.pubads());
    }*/

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

// Configure when ready
googletag.cmd.push(function() {
    try {
        ADS.setup_ads();
    } catch(e) {
        NPR.messaging.exception(e, 'Define Google Publisher Tags', NPR.messaging.constants.SPONSORSHIP_ERROR);
    }
});

// Render desktop ad if needed
if (ADS.shouldRenderForDevice('desktop')) {
    googletag.cmd.push(function() {
        googletag.display('ad-desktop');
    });
}

// Render mobile ad if needed
/*if (ADS.shouldRenderForDevice('mobile')) {
    // NB: Using ad slots for adhesion doesn't work for reasons that are unclear
    // The NPR.org homepage doesn't do it this way either
    googletag.cmd.push(function() {
        googletag.display('adhesion');
    });

    var ord = Math.floor(Math.random() * 1e16);
                
    // use the smaller size for phone, the larger size for tablet
    var size = '640x100';

    if (Modernizr.mq('only screen and (min-width: 768px)')) {
        size = '2048x180';
    }
    
    $('#adhesion').append('<scr' + 'ipt type="text/javascript" src="http://ad.doubleclick.net/N6735/adj/n6735.nprmobile/' + APP_CONFIG.NPR_DFP.TARGET + ';storyId=' + APP_CONFIG.NPR_DFP.STORY_ID + ';testserver=false;sz=' + size + ';ord=' + ord + '?"><\/script>');
}*/

// Load Google
ADS.setup_googletag();
