function AddNamespace(namespacePath) {
	var rootObject = window;
	var namespaceParts = namespacePath.split('.');
	for (var i = 0; i < namespaceParts.length; i++) {
		var currentPart = namespaceParts[i];
		if (!rootObject[currentPart]) {
			rootObject[currentPart] = new Object();
		}
		rootObject = rootObject[currentPart];
	}
}
AddNamespace('NPR.ServerConstants');
NPR.ServerConstants.webHost = 'apps.npr.org';
NPR.ServerConstants.dfpServer = 'ad.doubleclick.net';
NPR.ServerConstants.dfpNetwork = 'n6735';
NPR.ServerConstants.dfpSite = 'NPR';

AddNamespace('NPR.PageInfo');
NPR.PageInfo.page = {};
NPR.PageInfo.page.web_host = 'http://' + NPR.ServerConstants.webHost;
NPR.PageInfo.getUrlParameter = function (pname, pdefault) {
    try {
        pname = pname.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
        var regexS = "[\\?&]" + pname + "=([^&#]*)";
        var regex = new RegExp(regexS);
        var results = regex.exec(window.location.href);
        if (results === null) {
            return pdefault;
        } else {
            return results[1];
        }
    } catch (e) {
        // error
    }
};

AddNamespace('NPR.Devices');
if ('ontouchstart' in document.documentElement) {
	var winWidth = window.innerWidth;
	if (winWidth >= 768 && winWidth <= 1024) {
		$('html').addClass('NPRtablet');
	}
	if (winWidth <= 767) {
		$('html').addClass('NPRphone');
	}
    // No box ad when we have adhesion, so #header gets 12 columns
    if (winWidth <= 1024){
        $('#header').removeClass('span8').addClass('span12');
    }
}
if (NPR.PageInfo.getUrlParameter('device') == 'tablet') {
	$('html').addClass('NPRtablet');
}
if (NPR.PageInfo.getUrlParameter('device') == 'phone') {
	$('html').addClass('NPRphone');
}
NPR.Devices.isOnTablet = function () {
	if ($('html').hasClass('NPRtablet')) {
		return true;
	} else {
		return false;
	}
};
NPR.Devices.isOnPhone = function () {
	if ($('html').hasClass('NPRphone')) {
		return true;
	} else {
		return false;
	}
};
$(document).ready(function () {
	if (NPR.Devices.isOnTablet()) {
		setTimeout(function () {
			$('div[data-portrait]').each(function (index) {
				var newLocation = $(this).attr('data-portrait');
				$(this).children().not('script').clone().appendTo('#' + newLocation);
			});
		}, 500);
	}
});

var DFP = {};
DFP.tile = 0;
DFP.ord = Number(window.ord) || Math.floor(Math.random() * 1E10);

DFP.getParameterFromQueryString = function(strParamName) {
    var strReturn = "";
    var strHref = window.location.href;
    if ( strHref.indexOf("?") > -1 )
    {
        var strQueryString = strHref.substr(strHref.indexOf("?"));
        var aQueryString = strQueryString.split("&");
        for ( var iParam = 0; iParam < aQueryString.length; iParam++ )
        {
          if (aQueryString[iParam].indexOf(strParamName + "=") > -1 )
          {
            var aParam = aQueryString[iParam].split("=");
            strReturn = aParam[1];
            break;
          }
        }
    }
    return strReturn;
}

DFP.queryParameters = {sc: DFP.getParameterFromQueryString('sc'), ft: DFP.getParameterFromQueryString('ft')};

DFP.renderLocation = function(deviceEnv) {
    if (DFP.shouldRenderForDevice(deviceEnv)) {
        var scValue = '';
        var site = NPR.serverVars.DFPsite;

        var size = '300x250';
        var sponsorshiptext = '<p class="left">NPR thanks our sponsors</p><p class="right"><a href="/about/place/corpsupport/">Become an NPR sponsor</a></p>';
        if (NPR.Devices.isOnTablet()) {
            size = '2048x180';
            site = NPR.serverVars.DFPmobile;
            sponsorshiptext = '';
        }
        else if (NPR.Devices.isOnPhone()) {
            size = '640x100';
            site = NPR.serverVars.DFPmobile;
            sponsorshiptext = '';
        }

        if (typeof DFP.queryParameters.sc === 'string' && DFP.queryParameters.sc.length > 0) {
            scValue = DFP.queryParameters.sc;
        }
        else if (typeof document.referrer === 'string' && document.referrer.search('facebook.com') > -1) {
            scValue = 'fb';
        }
        else if (typeof DFP.queryParameters.ft === 'string') {
            scValue = DFP.queryParameters.ft;
        }

        var orient = '';
        if (NPR.Devices.isOnPhone() || NPR.Devices.isOnTablet()) {
            if (window.orientation == 0 || window.orientation == 180) {
                orient = 'portrait';
            } else if (window.orientation == 90 || window.orientation == -90) {
                orient = 'landscape';
            }
            orient = 'portrait'; /* FOR TESTING */
        }

        DFP.target = 'http://' + NPR.serverVars.DFPserver + '/adj/' + NPR.serverVars.DFPnetwork + '.' + site + NPR.serverVars.DFPtarget;

        var toRender = '<scr' + 'ipt src="'
            + DFP.target
            + ';sz=' + size
            + ';tile=' + (++DFP.tile)
            + ';sc=' + scValue
            + ';ord=' + DFP.ord
            + ';orient=' + orient
            + ';" type="text/javascript" language="javascript"></scr' + 'ipt>' + sponsorshiptext;

		//console.log(toRender);
		document.write(toRender);

        if (NPR.Devices.isOnPhone()) {
            $(document).ready(function() {
                $(window).bind('orientationchange', DFP.hideAdsOnOrientationChange);
            });
        }
    }
}

DFP.render88 = function(deviceEnv) {
    DFP.target = 'http://' + NPR.serverVars.DFPserver + '/adj/' + NPR.serverVars.DFPnetwork + '.' + NPR.serverVars.DFPsite + NPR.serverVars.DFPtarget;

    var toRender = '<scr' + 'ipt src="'
        + DFP.target
        + ';sz=88x31'
        + ';tile=' + (++DFP.tile)
        + ';ord=' + DFP.ord
        + ';" type="text/javascript" language="javascript"></scr' + 'ipt>';

    document.write(toRender);
}

DFP.hideAdsOnOrientationChange = function() {
    if (window.orientation == 90 || window.orientation == -90) {
        $('#adhesion').remove();
    }
}

DFP.shouldRenderForDevice = function(deviceEnv) {
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
                } else if (!NPR.Devices.isOnTablet() && winWidth > 1024) {
                    shouldRender = true;
                }
                
                break;
            case 'mobile':
                if ((NPR.Devices.isOnPhone() || NPR.Devices.isOnTablet()) && winWidth >= 300 && winWidth <= 1024) {
                    // block ads from ever showing on small-screen mobile devices
                    if (winWidth >= 480 || winOrientation == 0 || winOrientation == 180) {
//                        if (document.cookie.indexOf('sponsorcap') === -1) {
                            shouldRender = true;
//                            DFP.setCookieVal();
//                        } else {
//                            shouldRender = false;
//                        }
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

DFP.setCookieVal = function() {
    var date = new Date();
    date.setTime(date.getTime()+(60*1000));
    var expires = "; expires="+date.toGMTString();
    document.cookie = "sponsorcap=true"+expires+"; path=/";
}