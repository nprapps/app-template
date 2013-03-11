/*
 * A jQuery-ized Scribble Live plugin.
 *
 * Depends on jQuery, Underscore, auth.js,
 * app-chat.less and the JST chat templates.
 */

(function($) {
    $.livechat = function(element, options) {
        // Immutable configuration
        var NPR_AUTH_URL = 'https://api.npr.org/infinite/v1.0/login/';
        var JANRAIN_INFO_URL = 'https://rpxnow.com/api/v2/auth_info';
        var OAUTH_COOKIE_NAME = 'nprapps_chat_oauth';
        var SCRIBBLE_COOKIE_NAME = 'nprapps_chat_scribble';
        var SCRIBBLE_AUTH_EXPIRATION = 118;

        // Settings
        var defaults = {
            chat_id: null,
            chat_token: null,
            update_interval: 1000,
            alert_interval: 500,
            read_only: false,
            scribble_host: 'apiv1.scribblelive.com',
            posts_per_page: 50,
            filter_user_ids: [],
            is_filtered: false
        };

        var plugin = this;
        plugin.settings = {};
        plugin.$root = $(element);

        // State
        var chat_url = null;
        var page_url = null;
        var user_url = null;

        var since = null;
        var next_page_back = -1;
        var paging = false;

        var first_load = true;

        var update_timer = null;
        var paused = false;
        var is_live = false;

        plugin.init = function () {
            /*
             * Initialize the plugin.
             */
            plugin.settings = $.extend({}, defaults, options || {});

            chat_url = 'http://' + plugin.settings.scribble_host + '/event/' + plugin.settings.chat_id +'/all/';
            page_url = 'http://' + plugin.settings.scribble_host + '/event/' + plugin.settings.chat_id +'/page/';
            user_url = 'http://' + plugin.settings.scribble_host + '/user';

            // Cache element references
            // plugin.$chat_title = plugin.$root.find('.chat-title');
            // plugin.$chat_blurb = plugin.$root.find('.chat-blurb');
            plugin.$chat_body = plugin.$root.find('.chat-body');
            plugin.$alerts = plugin.$root.find('.chat-alerts');
            plugin.$chat_user_entry = plugin.$root.find('.chat-user-entry');
            plugin.$spinner = plugin.$root.find('.chat-spinner');

            plugin.$editor = plugin.$root.find('.chat-editor');
            plugin.$username = plugin.$editor.find('.chat-username');
            plugin.$comment = plugin.$editor.find('.chat-content');
            plugin.$comment_button = plugin.$editor.find('.chat-post');
            plugin.$logout = plugin.$editor.find('.chat-logout');
            plugin.$clear = plugin.$editor.find('.chat-clear');

            plugin.$login = plugin.$root.find('.chat-login');
            plugin.$anonymous = plugin.$login.find('button.anon');
            plugin.$oauth = plugin.$login.find('button.oauth');
            plugin.$npr = plugin.$login.find('button.npr');

            plugin.$anonymous_login_form = plugin.$root.find('.chat-anonymous-login');
            plugin.$anonymous_username = plugin.$anonymous_login_form.find('.chat-anonymous-username');
            plugin.$anonymous_login_button = plugin.$anonymous_login_form.find('button');

            plugin.$npr_login_form = plugin.$root.find('.chat-npr-login');
            plugin.$npr_username = plugin.$npr_login_form.find('.chat-npr-username');
            plugin.$npr_password = plugin.$npr_login_form.find('.chat-npr-password');
            plugin.$npr_login_button = plugin.$npr_login_form.find('button');

            plugin.$filter_all_posts = $('#chat-toggle');
            plugin.$filter_live_blog = $('#blog-toggle');

            // Setup event handlers
            plugin.$oauth.on('click', plugin.oauth_click);
            plugin.$anonymous.on('click', plugin.anonymous_click);
            plugin.$npr.on('click', plugin.npr_click);
            plugin.$logout.on('click', plugin.logout_click);
            plugin.$anonymous_login_button.on('click', plugin.anonymous_login_click);
            plugin.$npr_login_button.on('click', plugin.npr_login_click);
            plugin.$npr_username.keydown(function(e) { plugin.npr_login_enter_key(e); });
            plugin.$npr_password.keydown(function(e) { plugin.npr_login_enter_key(e); });
            plugin.$clear.on('click', plugin.clear_click);
            plugin.$comment_button.on('click', plugin.comment_click);

            plugin.$filter_all_posts.on('click', plugin.chat_filter_switched);
            plugin.$filter_live_blog.on('click', plugin.chat_filter_switched);

            // Initialize the user and the chat data.
            if (!plugin.settings.read_only) {
                plugin.toggle_user_context($.totalStorage(SCRIBBLE_COOKIE_NAME), false);
            }

            plugin.pause(false);

        };

        plugin.pause = function(new_paused) {
            plugin.paused = new_paused;

            if (plugin.paused) {
                clearTimeout(plugin.update_timer);

                $(window).off('scroll', plugin.debounce_scrolled);
            } else {
                plugin.update_live_chat();

                $(window).on('scroll', plugin.debounce_scrolled);
            }
        };

        plugin.clear_fields = function() {
            /*
             * Clear text entry fields.
             */
            plugin.$anonymous_username.val('');
            plugin.$npr_username.val('');
            plugin.$npr_password.val('');
            plugin.$comment.val('');
        };

        plugin.logout_user = function() {
            $.totalStorage(SCRIBBLE_COOKIE_NAME, null);
            plugin.clear_fields();
            plugin.toggle_user_context();
        };

        function strip_tags(str) {
            return str.replace(/(<([^>]+)>)/ig, '');
        }

        function _send_comment(text) {
            /*
             * Handles comment ajax.
             */
            var auth = $.totalStorage(SCRIBBLE_COOKIE_NAME);
            var content_param = '&Content=' + encodeURIComponent(text);
            var auth_param = '&Auth=' + auth.Auth;
            $.ajax({
                url: chat_url + '?Token=' + plugin.settings.chat_token + '&format=json' + content_param + auth_param,
                dataType: 'jsonp',
                jsonpCallback: 'nprapps_comment',
                cache: true,
                success: function(response) {
                    plugin.$comment.val('');
                    plugin.alert({
                        klass: 'alert-info',
                        title: null,
                        text: 'Your comment will appear momentarily.'
                    });
                }
            });
        }

        plugin.post_comment = function(data) {
            /*
             * If auth is good, post comment now. Otherwise, reauthenticate and then post comment.
            */
            if (plugin.validate_scribble_auth() === true) {
                _send_comment(data);
            } else {
                plugin.scribble_auth_user({
                    auth_route: 'anonymous',
                    username: $.totalStorage(SCRIBBLE_COOKIE_NAME).Name })
                .then(_send_comment(data));
            }
        };

        plugin.alert = function(context) {
            /*
             * Display an alert.
             * */
            var $alert = $(JST.chat_alert(context));
            plugin.$alerts.append($alert);

            setTimeout(function() {
                $alert.fadeOut();
            }, 3000);
        };

        plugin.render_post = function(post) {
            /*
            * Called once for each post.
            * Renders appropriate template for this post type.
            */

            // Decide if this post belongs to the logged-in user.
            post.Highlight = '';
            if ($.totalStorage(SCRIBBLE_COOKIE_NAME)) {
                if ($.totalStorage(SCRIBBLE_COOKIE_NAME).Id) {
                    if (post.Creator.Id === $.totalStorage(SCRIBBLE_COOKIE_NAME).Id) {
                        post.Highlight = 'highlighted';
                    }
                }
            }

            var m = moment(post.Created);
            post.timestamp = parseInt(m.valueOf(), 10);
            post.created_string = m.format('h:mm');

            if (m.hours() < 12) {
                post.created_string += ' a.m.';
            } else {
                post.created_string += ' p.m.';
            }

            post.filter_user = (_.indexOf(plugin.settings.filter_user_ids, post.Creator.Id) >= 0);
            post.visible = !plugin.settings.is_filtered || post.filter_user; 

            if (post.Type == "TEXT") {
                return JST.chat_text(post);
            } else if (post.Type == "IMAGE") {
                return JST.chat_image(post);
            } else {
                return '';
            }
        };

        plugin.filter_posts = function() {
            if (plugin.settings.is_filtered) {
                plugin.$chat_body.find('.chat-post').hide();
                plugin.$chat_body.find('.chat-post.filter-user').show();
            } else {
                plugin.$chat_body.find('.chat-post').show();
            }
        };

        plugin.render_new_posts = function(data) {
            /*
             * Render the latest posts from API data.
             */
            var new_posts = [];

            // Handle normal posts
            _.each(data.Posts, function(post) {
                var $exists = plugin.$chat_body.find('.chat-post[data-id="' + post.Id + '"]');

                if ($exists.length > 0) {
                    // Skip existing posts
                } else {
                    try {
                        var html = plugin.render_post(post);
                    } catch(err) {
                        return;
                    }

                    new_posts.push(html);
                }

                $exists = null;
            });

            if (new_posts.length > 0) {
                plugin.$chat_body.prepend(new_posts);
            }

            // Handle post deletes
            _.each(data.Deletes, function(post) {
                plugin.$chat_body.find('.chat-post[data-id="' + post.Id + '"]').remove();
            });

            _.each(data.Edits, function(post) {
                var html = plugin.render_post(post);

                plugin.$chat_body.find('.chat-post[data-id="' + post.Id + '"]').replaceWith(html);
            });
        };

        plugin.render_page_back = function(data) {
            /*
             * Render a page of posts from API data.
             */
            var new_posts = [];

            _.each(data.Posts, function(post) {
                try {
                    var html = plugin.render_post(post);
                } catch(err) {
                    return;
                }

                new_posts.push(html);
            });

            plugin.$spinner.before(new_posts);

            next_page_back -= 1;

            if (next_page_back == -1) {
                plugin.$spinner.remove();
                plugin.$spinner = null;
            }

        };

        plugin.scrolled = function() {
            var $window = $(window);

            if (plugin.$spinner && plugin.$spinner.offset().top < $window.scrollTop() + $window.height()) {
                plugin.page_back();
            }
        };

        plugin.debounce_scrolled = _.debounce(plugin.scrolled, 300);

        plugin.update_live_chat = function() {
            /*
             * Fetch latest posts and render them.
             */
            if (first_load) {
                var url = page_url + 'last?Token=' + plugin.settings.chat_token + '&Max=' + plugin.settings.posts_per_page + '&rand=' + Math.floor(Math.random() * 10000000);
            } else {
                var url = chat_url + '?Token=' + plugin.settings.chat_token + '&Max=' + plugin.settings.posts_per_page + '&rand=' + Math.floor(Math.random() * 10000000) + '&Since=' + since.format('YYYY/MM/DD HH:mm:ss');
            }

            $.ajax({
                url: url,
                dataType: 'jsonp',
                jsonpCallback: 'nprapps_latest',
                cache: true,
                success: function(data, status, xhr) {
                    if (parseInt(data.IsLive, 10) === 1) {
                        plugin.$chat_user_entry.show();
                    } else {
                        plugin.$chat_user_entry.hide();
                    }

                    since = moment.utc(data.LastModified).add('seconds', 1);

                    if (first_load) {
                        plugin.render_page_back(data);

                        next_page_back = data.Pages - 2;

                        // Always load one extra page
                        if (next_page_back > -1) {
                            plugin.page_back();
                        } else {
                            plugin.$spinner.remove();
                            plugin.$spinner = null;
                        }

                        first_load = false;
                    } else {
                        plugin.render_new_posts(data);
                    }
                }
            }).then(function() {
                if (!plugin.paused) {
                    plugin.update_timer = setTimeout(plugin.update_live_chat, plugin.settings.update_interval);
                }
            });
        };

        plugin.page_back = function() {
            // Prevent overlapping paging requests when things are slow
            if (paging) {
                return;
            }

            paging = true

            $.ajax({
                url: page_url + next_page_back + '?Token=' + plugin.settings.chat_token + '&Max=' + plugin.settings.posts_per_page + '&rand=' + Math.floor(Math.random() * 10000000),
                dataType: 'jsonp',
                jsonpCallback: 'nprapps_page_back',
                cache: true,
                success: function(data, status, xhr) {
                    plugin.render_page_back(data);
                }
            }).then(function() {
                paging = false;

                // We may not have loaded anything, so if spinner is still on screen, load more
                if (plugin.settings.is_filtered) {
                    $(window).trigger('scroll');
                }
            });
        };

        plugin.toggle_npr_login = function(visible) {
            /*
             * Toggle UI elements for NPR login.
             */
            plugin.$npr_login_form.toggle(visible);
            plugin.$npr.toggleClass('disabled', visible);
        };

        plugin.toggle_anonymous_login = function(visible) {
            /*
             * Toggle UI elements for anonymous login.
             */
            plugin.$anonymous_login_form.toggle(visible);
            plugin.$anonymous.toggleClass('disabled', visible);
        };

        plugin.validate_scribble_auth = function() {
            /*
            * Compares timestamps to validate a Scribble auth token.
            */
            if ($.totalStorage(SCRIBBLE_COOKIE_NAME)) {
                if ($.totalStorage(SCRIBBLE_COOKIE_NAME).Expires) {
                    if ( $.totalStorage(SCRIBBLE_COOKIE_NAME).Expires < moment() ) {
                        return false;
                    } else {
                        return true;
                    }
                }
            }
        };

        plugin.toggle_user_context = function(auth, reauthenticate) {
            /*
             * Show auth if not logged in, hide auth if logged in.
             * If reauthenticate is true, get new credentials from Scribble.
             */
            var visible = (auth !== undefined && auth !== null);

            if (visible) {
                plugin.$username.text(auth.Name);

                if (reauthenticate === true) {
                    if (plugin.validate_scribble_auth() === false) {
                        plugin.scribble_auth_user({ auth_route: 'anonymous', username: $.totalStorage(SCRIBBLE_COOKIE_NAME).Name });
                    }
                }
            }

            plugin.$login.toggle(!visible);
            plugin.$editor.toggle(visible);
       };

        plugin.scribble_auth_user = function(data) {
            /*
             * Login to Scribble with username we got from [Facebook|Google|NPR|etc].
             */
            var auth_url = user_url +'/create?Token='+ plugin.settings.chat_token;

            if (data.username == '') {
                plugin.alert({
                    klass: 'alert-error',
                    title: 'Login failed!',
                    text: 'You must provide a username.'
                });

                return;
            }

            if (data.auth_route === 'anonymous' || data.auth_route === 'oauth') {
                return $.ajax({
                    url: auth_url + '&format=json&Name='+ data.username +'&Avatar='+ data.avatar,
                    dataType: 'jsonp',
                    cache: true,
                    success: function(auth) {
                        auth.Expires = moment().add('minutes', SCRIBBLE_AUTH_EXPIRATION).valueOf();
                        $.totalStorage(SCRIBBLE_COOKIE_NAME, auth);
                        plugin.clear_fields();
                        plugin.toggle_user_context($.totalStorage(SCRIBBLE_COOKIE_NAME), false);
                    }
                });
            }
        };

        plugin.npr_auth_user = function() {
            /*
            * Authorizes an NPR user.
            */
            var username = plugin.$npr_username.val();
            var password = plugin.$npr_password.val();

            if (username == '' || password == '') {
                plugin.alert({
                    klass: 'alert-error',
                    title: 'Login failed!',
                    text: 'You must provide an email and password.'
                });

                return;
            }

            var payload = { username: username, password: password, remember: null, temp_user: null };
            var b64_payload = window.btoa(JSON.stringify(payload));

            $.ajax({
                url: NPR_AUTH_URL,
                dataType: 'jsonp',
                type: 'POST',
                crossDomain: true,
                cache: false,
                timeout: 4000,
                data: { auth: b64_payload, platform: 'CRMAPP' },
                success: function(response) {
                    $.totalStorage(OAUTH_COOKIE_NAME, response.user_data);
                    plugin.scribble_auth_user({ auth_route: 'anonymous', username: response.user_data.nick_name });
                    plugin.toggle_user_context(OAUTH_COOKIE_NAME, true);
                },
                error: function() {
                    plugin.alert({
                        klass: 'alert-error',
                        title: 'Login failed!',
                        text: 'Your email or password was incorrect.'
                    });
                }
            });
        };

        plugin.oauth_callback = function(response) {
            /*
             * Authenticate and intialize user.
             */
            if (response.status === 'success') {
                $.totalStorage(OAUTH_COOKIE_NAME, response.user_data);
                plugin.scribble_auth_user({ auth_route: 'anonymous', username: response.user_data.nick_name });
                plugin.toggle_user_context(OAUTH_COOKIE_NAME, true);
            }
        };

        // Event handlers
        plugin.oauth_click = function() {
            NPR_AUTH.login($(this).attr('data-service'), plugin.oauth_callback);
            plugin.toggle_anonymous_login(false);
            plugin.toggle_npr_login(false);
        };

        plugin.anonymous_click = function() {
            plugin.toggle_anonymous_login(true);
            plugin.toggle_npr_login(false);
        };

        plugin.npr_click = function() {
            plugin.toggle_anonymous_login(false);
            plugin.toggle_npr_login(true);
        };

        plugin.logout_click = function() {
            plugin.logout_user();
            plugin.toggle_anonymous_login(false);
            plugin.toggle_npr_login(false);
        };

        plugin.anonymous_login_click = function() {
            plugin.scribble_auth_user({ auth_route: 'anonymous', username: plugin.$anonymous_username.val() });
        };

        plugin.npr_login_click = function() {
            plugin.npr_auth_user();
        };

        plugin.npr_login_enter_key = function(e) {
            if (e.keyCode == 13) {
                plugin.npr_auth_user();
            }
        };

        plugin.clear_click = function() {
            plugin.clear_fields();
        };

        plugin.comment_click = function() {
            var safe_comment = strip_tags(plugin.$comment.val());
            plugin.post_comment(safe_comment);
        };

        plugin.toggle_filtering = function(filter) {
            plugin.settings.is_filtered = filter;
            plugin.filter_posts();
        };

        plugin.init();
    };

    $.fn.livechat = function(options) {
        return this.each(function() {
            if ($(this).data('livechat') === undefined) {
                var plugin = new $.livechat(this, options);
                $(this).data('livechat', plugin);
            }
        });
    };
}(jQuery));
