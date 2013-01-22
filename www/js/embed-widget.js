if(window.station == undefined) {
    window.station = '';
}

var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src=\'" + gaJsHost + "google-analytics.com/ga.js\' type=\'text/javascript\'%3E%3C/script%3E"));

try {
        var pageTracker = _gat._getTracker("UA-5828686-3");
        pageTracker._setDomainName("none");
        pageTracker._setAllowLinker(true);
        pageTracker._setCustomVar(1,"Module","TODO",3);
        pageTracker._trackPageview();
} catch(err) {}


/* check for user-defined width */
try {
	if (nprapps_widget_width) {}
} catch (err) {
	nprapps_widget_width = '300';
}

try {
	if (nprapps_widget_height) {}
} catch (err) {
	nprapps_widget_height = '500';
}

document.write(
'<script type="text/javascript">window.vsitag = {"imp":"TODO"};</script>',
'<script type="text/javascript" language="javascript" src="http://www.npr.org/include/javascript/zigi.js"></script>',
'<iframe src="widget.html?station=' + window.station + '" width="' + nprapps_widget_width + '" height="' + nprapps_widget_height + '" scrolling="auto" marginheight="0" marginwidth="0" frameborder="0" style="border: 1px solid #CCC;" ></iframe>',
'');
