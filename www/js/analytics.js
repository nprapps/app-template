/*
 * Google Analytics
 */
var _gaq = _gaq || [];
_gaq.push(['_setAccount', APP_CONFIG.GOOGLE_ANALYTICS.ACCOUNT_ID]);
_gaq.push(['_setDomainName', APP_CONFIG.GOOGLE_ANALYTICS.DOMAIN]);
//_gaq.push(['_setCustomVar', 1, 'BC', '', 3]);
_gaq.push(['_setCustomVar', 2, 'Topics', APP_CONFIG.GOOGLE_ANALYTICS.TOPICS, 3]);
//_gaq.push(['_setCustomVar', 3, 'Program ID', '', 3]);
//_gaq.push(['_setCustomVar', 3, 'Localization', '', 1]);
_gaq.push(['_setCustomVar', 4, 'OrgID', '1', 3]);
_gaq.push(['_setCustomVar', 5, 'Page Types', '1', 3]);

var orientation = 'portrait';

if (window.orientation == 90 || window.orientation == -90) {
    orientation = 'landscape';
}

_gaq.push(['_setCustomVar', 6, 'Orientation', orientation, 3]);

var viewportSize = $(window).width();
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

(function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();

/*
 * Comscore
 */
var _comscore = _comscore || [];
_comscore.push({ c1: "2", c2: "17691522" });
(function() {
    var s = document.createElement("script"), el = document.getElementsByTagName("script")[0]; s.async = true;
    s.src = (document.location.protocol == "https:" ? "https://sb" : "http://b") + ".scorecardresearch.com/beacon.js";
    el.parentNode.insertBefore(s, el);
})();

/*
 * Nielson
 */
(function () {
    var d = new Image(1, 1);
    d.onerror = d.onload = function () { d.onerror = d.onload = null; };
    d.src = ["//secure-us.imrworldwide.com/cgi-bin/m?ci=us-803244h&cg=0&cc=1&si=", escape(window.location.href), "&rp=", escape(document.referrer), "&ts=compact&rnd=", (new Date()).getTime()].join('');
})();   

/*
 * Chartbeat
 */
var _sf_async_config={};
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

