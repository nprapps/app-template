/*
 * Module for tracking standardized analytics.
 */

var _gaq = _gaq || [];
var _sf_async_config = {};
var _comscore = _comscore || [];

var ANALYTICS = (function () {

    // Global time tracking variables
    var slideStartTime =  new Date();
    var timeOnLastSlide = null;

    /*
     * Google Analytics
     */
    var setupGoogle = function() {
        _gaq.push(['_setAccount', APP_CONFIG.NPR_GOOGLE_ANALYTICS.ACCOUNT_ID]);
        _gaq.push(['_setDomainName', APP_CONFIG.NPR_GOOGLE_ANALYTICS.DOMAIN]);
        //_gaq.push(['_setCustomVar', 1, 'BC', '', 3]);
        _gaq.push(['_setCustomVar', 2, 'Topics', APP_CONFIG.NPR_GOOGLE_ANALYTICS.TOPICS, 3]);
        //_gaq.push(['_setCustomVar', 3, 'Program ID', '', 3]);
        //_gaq.push(['_setCustomVar', 3, 'Localization', '', 1]);
        _gaq.push(['_setCustomVar', 4, 'OrgID', '1', 3]);
        _gaq.push(['_setCustomVar', 5, 'Page Types', '1', 3]);

        var orientation = 'portrait';

        if (window.orientation == 90 || window.orientation == -90) {
            orientation = 'landscape';
        }

        _gaq.push(['_setCustomVar', 6, 'Orientation', orientation, 3]);

        var viewportSize = document.body.clientWidth;
        var viewportGrouping = '1760 and higher';

        if (viewportSize < 481) {
            viewportGrouping = '0 - 480';
        } else if (viewportSize < 768) {
            viewportGrouping = '481 - 767';
        } else if (viewportSize < 1000) {
            viewportGrouping = '768 - 999';
        } else if (viewportSize < 1201) {
            viewportGrouping = '1000 - 1200';
        } else if (viewportSize < 1760) {
            viewportGrouping = '1201 - 1759';
        }

        _gaq.push(['_setCustomVar', 7, 'Viewport Size', viewportGrouping, 3]);

        if (typeof window.devicePixelRatio !== 'undefined' && window.devicePixelRatio >= 1.5) {
            _gaq.push(['_setCustomVar', 10, 'High Density Displays', 'High', 2]);
        } else {
            _gaq.push(['_setCustomVar', 10, 'High Density Displays', 'Low', 2]);
        }

        if ('ontouchstart' in document.documentElement) {
            _gaq.push(['_setCustomVar', 11, 'Touch screens', 'Touch', 2]);
        } else {
            _gaq.push(['_setCustomVar', 11, 'Touch screens', 'Traditional', 2]);
        }

        _gaq.push(['_trackPageview']);

        // Old GA: NPR.org
        (function() {
            var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
            ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
            var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
        })();

        // New GA: NPR Visuals
        (function(i,s,o,g,r,a,m) {
            i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
            (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
            m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
        })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

        ga('create', APP_CONFIG.VIZ_GOOGLE_ANALYTICS.ACCOUNT_ID, 'auto');
        ga('send', 'pageview');
     }

    /*
     * Comscore
     */
    var setupComscore = function() {
        _comscore.push({ c1: "2", c2: "17691522" });

        (function() {
            var s = document.createElement("script"), el = document.getElementsByTagName("script")[0]; s.async = true;
            s.src = (document.location.protocol == "https:" ? "https://sb" : "http://b") + ".scorecardresearch.com/beacon.js";
            el.parentNode.insertBefore(s, el);
        })();
    }

    /*
     * Nielson
     */
    var setupNielson = function() {
        (function () {
            var d = new Image(1, 1);
            d.onerror = d.onload = function () { d.onerror = d.onload = null; };
            d.src = ["//secure-us.imrworldwide.com/cgi-bin/m?ci=us-803244h&cg=0&cc=1&si=", escape(window.location.href), "&rp=", escape(document.referrer), "&ts=compact&rnd=", (new Date()).getTime()].join('');
        })();
    }

    /*
     * Chartbeat
     */
    var setupChartbeat = function() {
        /** CONFIGURATION START **/
        _sf_async_config.uid = 18888;
        _sf_async_config.domain = "npr.org";
        /** CONFIGURATION END **/
        (function(){
            function loadChartbeat() {
                window._sf_endpt=(new Date()).getTime();
                var e = document.createElement("script");
                e.setAttribute("language", "javascript");
                e.setAttribute("type", "text/javascript");
                e.setAttribute("src",
                    (("https:" == document.location.protocol) ?
                     "https://a248.e.akamai.net/chartbeat.download.akamai.com/102508/" :
                     "http://static.chartbeat.com/") +
                    "js/chartbeat.js");
                document.body.appendChild(e);
            }
            var oldonload = window.onload;
            window.onload = (typeof window.onload != "function") ?
                loadChartbeat : function() { oldonload(); loadChartbeat(); };
        })();
    }

    /*
     * Event tracking.
     */
    var trackEvent = function(eventName, label, value) {
        var eventData = {
            'hitType': 'event',
            'eventCategory': APP_CONFIG.PROJECT_SLUG,
            'eventAction': eventName
        }

        if (label) {
            eventData['eventLabel'] = label;
        }

        if (value) {
            eventData['eventValue'] = value
        }

        ga('send', eventData);
    }

    // SHARING

    var openShareDiscuss = function() {
        trackEvent('open-share-discuss');
    }

    var closeShareDiscuss = function() {
        trackEvent('close-share-discuss');
    }

    var clickTweet = function(location) {
        trackEvent('tweet', location);
    }

    var clickFacebook = function(location) {
        trackEvent('facebook', location);
    }

    var clickEmail = function(location) {
        trackEvent('email', location);
    }

    var postComment = function() {
        trackEvent('new-comment');
    }

    var actOnFeaturedTweet = function(action, tweet_url) {
        trackEvent('featured-tweet-action', action, null);
    }

    var actOnFeaturedFacebook = function(action, post_url) {
        trackEvent('featured-facebook-action', action, null);
    }

    var copySummary = function() {
        trackEvent('summary-copied');
    }

    // NAVIGATION
    var usedKeyboardNavigation = false;

    var useKeyboardNavigation = function() {
        if (!usedKeyboardNavigation) {
            trackEvent('keyboard-nav');
            usedKeyboardNavigation = true;
        }
    }

    var completeTwentyFivePercent =  function() {
        trackEvent('completion', '0.25');
    }

    var completeFiftyPercent =  function() {
        trackEvent('completion', '0.5');
    }

    var completeSeventyFivePercent =  function() {
        trackEvent('completion', '0.75');
    }

    var completeOneHundredPercent =  function() {
        trackEvent('completion', '1');
    }

    var startFullscreen = function() {
        trackEvent('fullscreen-start');
    }

    var stopFullscreen = function() {
        trackEvent('fullscreen-stop');
    }

    var begin = function(location) {
        trackEvent('begin', location);
    }

    var readyChromecast = function() {
        trackEvent('chromecast-ready');
    }

    var startChromecast = function() {
        trackEvent('chromecast-start');
    }

    var stopChromecast = function() {
        trackEvent('chromecast-stop');
    }

    // SLIDES

    var exitSlide = function(slide_index) {
        var currentTime = new Date();
        timeOnLastSlide = Math.abs(currentTime - slideStartTime);
        slideStartTime = currentTime;
        trackEvent('slide-exit', slide_index, timeOnLastSlide);
    }

    setupGoogle();
    setupComscore();
    setupNielson();

    return {
        'setupChartbeat': setupChartbeat,
        'trackEvent': trackEvent,
        'openShareDiscuss': openShareDiscuss,
        'closeShareDiscuss': closeShareDiscuss,
        'clickTweet': clickTweet,
        'clickFacebook': clickFacebook,
        'clickEmail': clickEmail,
        'postComment': postComment,
        'actOnFeaturedTweet': actOnFeaturedTweet,
        'actOnFeaturedFacebook': actOnFeaturedFacebook,
        'copySummary': copySummary,
        'useKeyboardNavigation': useKeyboardNavigation,
        'completeTwentyFivePercent': completeTwentyFivePercent,
        'completeFiftyPercent': completeFiftyPercent,
        'completeSeventyFivePercent': completeSeventyFivePercent,
        'completeOneHundredPercent': completeOneHundredPercent,
        'exitSlide': exitSlide,
        'startFullscreen': startFullscreen,
        'stopFullscreen': stopFullscreen,
        'begin': begin,
        'readyChromecast': readyChromecast,
        'startChromecast': startChromecast,
        'stopChromecast': stopChromecast
    };
}());
