/*
 * Event handling for the share discuss panel.
 */

var SHARE = (function () {
	var $shareModal = null;
	var $clippy = null;
	var $email = null;
	var $facebook = null;
	var $twitter = null;

	var setup = function() {
		$shareModal = $('#share-modal');
		$clippy = $shareModal.find('.clippy');	
		$email = $shareModal.find('.email-friend a');
		$facebook = $shareModal.find('.facebook-share a');
		$twitter = $shareModal.find('.twitter-share a');

	    $shareModal.on('shown.bs.modal', onShareModalShown);
	    $shareModal.on('hidden.bs.modal', onShareModalHidden);
	    $email.on('click', onEmailClick);
	    $facebook.on('click', onFacebookClick);
	    $twitter.on('click', onTwitterClick);

	    // configure ZeroClipboard on share panel
	    ZeroClipboard.config({ swfPath: 'js/lib/ZeroClipboard.swf' });
	    var clippy = new ZeroClipboard($clippy);

	    clippy.on('ready', function(readyEvent) {
	        clippy.on('aftercopy', onClippyCopy);
	    });    
	}

	/*
	 * Share modal opened.
	 */
	var onShareModalShown = function() {
		ANALYTICS.openShareDiscuss();
	}

	/*
	 * Share modal closed.
	 */
	var onShareModalHidden = function() {
		ANALYTICS.closeShareDiscuss();
	}

	/*
	 * Text copied to clipboard.
	 */
	var onClippyCopy = function() {
	    alert('Copied to your clipboard!');

	    ANALYTICS.copySummary();
	}

	/*
	 * Email share clicked.
	 */
	var onEmailClick = function() {
		ANALYTICS.clickEmail('share-discuss');
	}

	/*
	 * Facebook share clicked.
	 */
	var onFacebookClick = function() {
		ANALYTICS.clickFacebook('share-discuss');
	}

	/*
	 * Twitter share clicked.
	 */
	var onTwitterClick = function() {
		ANALYTICS.clickTweet('share-discuss');
	}

    return {
        'setup': setup
    };
}());

