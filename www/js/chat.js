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
        var OAUTH_KEY = 'oauthKey0';
        var SCRIBBLE_AUTH_KEY = 'testAuth4';
        var SCRIBBLE_AUTH_EXPIRATION = 118;

        // Settings
        var defaults = {
            chat_id: null,
            chat_token: null,
            update_interval: 1000,
            alert_interval: 500,
            read_only: false,
            scribble_host: 'apiv1.scribblelive.com',
            posts_per_page: 50
        };

        var plugin = this;
        plugin.settings = {};
        plugin.$root = $(element);

        // State
        var chat_url = null;
        var user_url = null;

        var posts_on_load = [];
        var edits = [];

        var post_ids = [];
        var edit_ids = [];
        var delete_ids = [];

        var edit_timestamps = {};

        var alerts = [];
        var first_load = true;
        var next_page_index = 0;

        var update_timer = null;
        var alert_timer = null;
        var paused = false;
        var is_live = false;

        plugin.init = function () {
            /*
             * Initialize the plugin.
             */
            plugin.settings = $.extend({}, defaults, options || {});

            chat_url = 'http://' + plugin.settings.scribble_host + '/event/' + plugin.settings.chat_id +'/all/?Token='+ plugin.settings.chat_token +'&format=json';
            user_url = 'http://' + plugin.settings.scribble_host + '/user';

            // Render
            plugin.$root.html(JST.chat());

            // Cache element references
            // plugin.$chat_title = plugin.$root.find('.chat-title');
            // plugin.$chat_blurb = plugin.$root.find('.chat-blurb');
            plugin.$chat_body = plugin.$root.find('.chat-body');
            plugin.$alerts = plugin.$root.find('.chat-alerts');
            plugin.$chat_form = plugin.$root.find('.chat-user-entry');
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

            // Setup event handlers
            plugin.$oauth.on('click', plugin.oauth_click);
            plugin.$anonymous.on('click', plugin.anonymous_click);
            plugin.$npr.on('click', plugin.npr_click);
            plugin.$logout.on('click', plugin.logout_click);
            plugin.$anonymous_login_button.on('click', plugin.anonymous_login_click);
            plugin.$npr_login_button.on('click', plugin.npr_login_click);
            plugin.$clear.on('click', plugin.clear_click);
            plugin.$comment_button.on('click', plugin.comment_click);

            // Initialize the user and the chat data.
            if (!plugin.settings.read_only) {
                plugin.toggle_user_context($.totalStorage(SCRIBBLE_AUTH_KEY), false);
            }

            plugin.pause(false);

        };

        plugin.pause = function(new_paused) {
            plugin.paused = new_paused;

            if (plugin.paused) {
                clearTimeout(plugin.update_timer);
                clearTimeout(plugin.alert_timer);

                $(window).off('scroll', plugin.debounce_scrolled);
            } else {
                plugin.update_live_chat();
                plugin.update_alerts();

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
            $.totalStorage(SCRIBBLE_AUTH_KEY, null);
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
            var auth = $.totalStorage(SCRIBBLE_AUTH_KEY);
            var content_param = '&Content=' + encodeURIComponent(text);
            var auth_param = '&Auth=' + auth.Auth;
            $.ajax({
                url: chat_url + content_param + auth_param,
                dataType: 'jsonp',
                cache: true,
                success: function(response) {
                    plugin.$comment.val('');
                    alerts.push({
                      klass: 'alert-info',
                      title: 'Awaiting moderation!',
                      text: 'Your comment is awaiting moderation.'
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
                    username: $.totalStorage(SCRIBBLE_AUTH_KEY).Name })
                .then(_send_comment(data));
            }
        };

        plugin.update_alerts = function() {
            /*
            * Adds and expires alerts.
            */

            // Expires old alerts with each pass.
            var now = parseInt(moment().valueOf(), 10);
            _.each($('div.alert'), function(alert_div, index, list) {
                var expires = alert_div.getAttribute('data-expires');
                if (now > expires) {
                    $(alert_div).fadeOut();
                }
            });

            // Adds any new alerts with each pass.
            _.each(alerts, function(alert, index, list) {
                alerts = [];
                alert.expires = parseInt(moment().add('seconds', 3).valueOf(), 10);
                alert_html = JST.alert({ alert: alert });
                plugin.$alerts.append(alert_html);
            });

            // Ignore if paused.
            if (!plugin.paused) {
                plugin.alerts_timer = setTimeout(plugin.update_alerts, plugin.settings.alert_interval);
            }
        };

        plugin.render_post = function(post) {
            /*
            * Called once for each post.
            * Renders appropriate template for this post type.
            */

            // Decide if this post belongs to the logged-in user.
            post.Highlight = '';
            if ($.totalStorage(SCRIBBLE_AUTH_KEY)) {
                if ($.totalStorage(SCRIBBLE_AUTH_KEY).Id) {
                    if (post.Creator.Id === $.totalStorage(SCRIBBLE_AUTH_KEY).Id) {
                        post.Highlight = ' highlighted';
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

            if (post.Type == "TEXT") {
                return JST.chat_text(post);
            } else if (post.Type == "IMAGE") {
                return JST.chat_image(post);
            } else {
                throw 'Unsupported post type.';
            }
        };

        plugin.render_new_posts = function(data) {
            /*
             * Render the latest posts from API data.
             */
            var scroll_down = false;
            var new_posts = [];

            // Handle normal posts
            _.each(data.Posts, function(post) {
                // Filter posts we've seen before
                if (_.indexOf(post_ids, post.Id) >= 0) {
                    return;
                }

                try {
                    var html = plugin.render_post(post);
                } catch(err) {
                    return;
                }

                new_posts.push(html);
                post_ids.push(post.Id);
            });

            if (new_posts.length > 0) {
                plugin.$chat_body.prepend(new_posts);

                scroll_down = true;
            }

            // Handle post deletes
            _.each(data.Deletes, function(post) {
                if (_.indexOf(delete_ids, post.Id) >= 0) {
                    return;
                }

                delete_ids.push(post.Id);

                plugin.$chat_body.find('.chat-post[data-id="' + post.Id + '"]').remove();
            });

            _.each(data.Edits, function(post) {
                var exists = _.indexOf(edit_ids, post.Id);

                if (exists >= 0) {
                    edits[exists] = post;

                    return;
                }

                edit_ids.push(post.Id);
                edits.push(post);
            });

            plugin.process_edits();

            if (scroll_down) {
                plugin.$chat_body.scrollTop(plugin.$chat_body[0].scrollHeight);
            }
        };

        plugin.process_edits = function() {
            /*
             * Process edits, replacing and inserting them as needed.
             *
             * NB: For simplicity we do this on every update.
             */
            _.each(edits, function(post) {
                var timestamp = parseInt(moment(post.LastModified).valueOf(), 10);

                var html = plugin.render_post(post);

                var $existing = plugin.$chat_body.find('.chat-post[data-id="' + post.Id + '"]');

                // Updating a post already displayed
                if ($existing.length > 0) {
                    if (post.Id in edit_timestamps && edit_timestamps[post.Id] >= timestamp) {
                        return;
                    }

                    $existing.replaceWith(html);
                    edit_timestamps[post.Id] = timestamp;
                // Updating a post never seen before (e.g. on page load)
                } else {
                    var $posts = plugin.$chat_body.find('.chat-post');
                    var $post = null;

                    var comes_before = _.find($posts, function(post_el, i) {
                        $post = $(post_el);

                        if (post.timestamp > parseInt($post.data('timestamp'), 10)) {
                            edit_timestamps[post.Id] = timestamp;
                            $post.before(html);

                            return true;
                        }

                        return false;
                    });

                    // If no place in the order, put at the end
                    if (!comes_before && next_page_index >= posts_on_load.length) {
                        edit_timestamps[post.Id] = timestamp;
                        if ($post === null) {
                            plugin.$chat_body.append(html);
                        } else {
                            $post.after(html);
                        }
                    }
                }
            });
        };

        plugin.render_post_page = function() {
            /*
             * Render a page of posts from API data.
             */
            var new_posts = [];
            var start = next_page_index;
            var end = next_page_index + plugin.settings.posts_per_page;

            // Handle normal posts
            _.each(posts_on_load.slice(start, end), function(post) {
                try {
                    var html = plugin.render_post(post);
                } catch(err) {
                    return;
                }

                new_posts.push(html);
            });

            if (new_posts.length > 0) {
                plugin.$spinner.before(new_posts);
            }

            plugin.process_edits();

            next_page_index += plugin.settings.posts_per_page;

            if (next_page_index >= posts_on_load.length) {
                plugin.$spinner.remove();
                plugin.$spinner = null;
            }
        };

        plugin.scrolled = function() {
            var $window = $(window);

            if (plugin.$spinner && plugin.$spinner.offset().top < $window.scrollTop() + $window.height()) {
                plugin.render_post_page();
            }
        };

        plugin.debounce_scrolled = _.debounce(plugin.scrolled, 300);

        plugin.update_live_chat = function() {
            /*
             * Fetch latest posts and render them.
             */
            $.ajax({
                url: chat_url + '&Max=10000&Order=desc',
                dataType: 'jsonp',
                cache: true,
                success: function(data, status, xhr) {
                    if (parseInt(data.IsLive, 10) === 1) {
                        plugin.$chat_form.show();
                        $('#chat-toggle .live').show();
                        $('#chat-toggle .pregame').hide();
                        $('#live-chat-widget-wrapper').hide();
                    } else {
                        plugin.$chat_form.hide();
                        $('#chat-toggle .pregame').show();
                        $('#chat-toggle .live').hide();
                        $('#live-chat-widget-wrapper').hide();
                    }

                    if (first_load) {
                        // plugin.$root.find('.chat-title').text(data.Title);
                        // plugin.$chat_blurb.text(data.Description);

                        posts_on_load = data.Posts;
                        post_ids = _.pluck(posts_on_load, 'Id');

                        edits = data.Edits;
                        edit_ids = _.pluck(edits, 'Id');

                        plugin.render_post_page();
                        plugin.$chat_body.scrollTop(plugin.$chat_body[0].scrollHeight);

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
            if ($.totalStorage(SCRIBBLE_AUTH_KEY)) {
                if ($.totalStorage(SCRIBBLE_AUTH_KEY).Expires) {
                    if ( $.totalStorage(SCRIBBLE_AUTH_KEY).Expires < moment() ) {
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
                        plugin.scribble_auth_user({ auth_route: 'anonymous', username: $.totalStorage(SCRIBBLE_AUTH_KEY).Name });
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

            if ((data.auth_route === 'anonymous' && data.username !== '') || (data.auth_route === 'oauth')) {
                return $.ajax({
                    url: auth_url +'&format=json&Name='+ data.username +'&Avatar='+ data.avatar,
                    dataType: 'jsonp',
                    cache: true,
                    success: function(auth) {
                        auth.Expires = moment().add('minutes', SCRIBBLE_AUTH_EXPIRATION).valueOf();
                        $.totalStorage(SCRIBBLE_AUTH_KEY, auth);
                        plugin.clear_fields();
                        plugin.toggle_user_context($.totalStorage(SCRIBBLE_AUTH_KEY), false);
                    }
                });
            }
            else {
                alert('Missing something. Try filling out the form again.');
            }
        };

        plugin.npr_auth_user = function() {
            /*
            * Authorizes an NPR user.
            */
            var payload = { username: plugin.$npr_username.val(), password: plugin.$npr_password.val(), remember: null, temp_user: null };
            var b64_payload = window.btoa(JSON.stringify(payload));

            $.ajax({
                url: NPR_AUTH_URL,
                dataType: 'jsonp',
                type: 'POST',
                crossDomain: true,
                cache: false,
                timeout: 2500,
                data: { auth: b64_payload, platform: 'CRMAPP' },
                success: function(response) {
                    $.totalStorage(OAUTH_KEY, response.user_data);
                    plugin.scribble_auth_user({ auth_route: 'anonymous', username: response.user_data.nick_name });
                    plugin.toggle_user_context(OAUTH_KEY, true);
                }
            });
        };

        plugin.oauth_callback = function(response) {
            /*
             * Authenticate and intialize user.
             */
            if (response.status === 'success') {
                $.totalStorage(OAUTH_KEY, response.user_data);
                plugin.scribble_auth_user({ auth_route: 'anonymous', username: response.user_data.nick_name });
                plugin.toggle_user_context(OAUTH_KEY, true);
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

        plugin.clear_click = function() {
            plugin.clear_fields();
        };

        plugin.comment_click = function() {
            var safe_comment = strip_tags(plugin.$comment.val());
            plugin.post_comment(safe_comment);
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
