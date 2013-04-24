#!/usr/bin/env python

import datetime
import logging
import os
import re
import time

from flask import Flask, redirect, render_template
from jinja2.filters import escape, do_mark_safe
from tumblpy import Tumblpy
from tumblpy import TumblpyError
from werkzeug import secure_filename

import app_config

app = Flask(app_config.PROJECT_NAME)
app.config['PROPAGATE_EXCEPTIONS'] = True

os.environ['TZ'] = 'US/Eastern'
time.tzset()

logger = logging.getLogger('tumblr')
file_handler = logging.FileHandler('/var/log/%s.log' % app_config.PROJECT_SLUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


@app.route('/%s/test/' % app_config.PROJECT_SLUG, methods=['GET'])
def _test_app():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


@app.route('/%s/' % app_config.PROJECT_SLUG, methods=['POST'])
def _post_to_tumblr():
    """
    Handles the POST to Tumblr.
    """

    def strip_html(value):
        """
        Strips HTML from a string.
        """
        return re.compile(r'</?\S([^=]*=(\s*"[^"]*"|\s*\'[^\']*\'|\S*)|[^>])*?>', re.IGNORECASE).sub('', value)

    def strip_breaks(value):
        """
        Converts newlines, returns and other breaks to <br/>.
        """
        value = re.sub(r'\r\n|\r|\n', '\n', value)
        return value.replace('\n', do_mark_safe('<br/>'))

    # Request is a global. Import it down here where we need it.
    from flask import request

    # These should match the form fields.
    message = strip_html(request.form.get('message', None))
    message = escape(message)
    message = strip_breaks(message)

    name = strip_html(request.form.get('signed_name', None))
    email = strip_html(request.form.get('email', None))

    context = {
        'message': message,
        'name': name,
        'email': email,
        'app_config': app_config
    }

    caption = render_template('caption.html', **context)

    secrets = app_config.get_secrets()
    t = Tumblpy(
        app_key=secrets['TUMBLR_APP_KEY'],
        app_secret=secrets['TUMBLR_APP_SECRET'],
        oauth_token=secrets['TUMBLR_OAUTH_TOKEN'],
        oauth_token_secret=secrets['TUMBLR_OAUTH_TOKEN_SECRET'])

    file_path = '/uploads/%s/%s_%s' % (
        app_config.PROJECT_SLUG,
        str(time.mktime(datetime.datetime.now().timetuple())).replace('.', ''),
        secure_filename(request.files['image'].filename.replace(' ', '-'))
    )

    with open('/var/www%s' % file_path, 'w') as f:
        f.write(request.files['image'].read())

    params = {
        "type": "photo",
        "caption": caption,
        "tags": app_config.TUMBLR_TAGS,
        "source": "http://%s%s" % (app_config.SERVERS[0], file_path)
    }

    try:
        tumblr_post = t.post('post', blog_url=app_config.TUMBLR_URL, params=params)
        tumblr_url = u"http://%s/%s" % (app_config.TUMBLR_URL, tumblr_post['id'])
        logger.info('200 %s reader(%s %s) (times in EST)' % (tumblr_url, name, email))

        return redirect(tumblr_url, code=301)

    except TumblpyError, e:
        logger.error('%s %s http://%s%s reader(%s %s) (times in EST)' % (
            e.error_code, e.msg, app_config.SERVERS[0], file_path, name, email))
        return 'TUMBLR ERROR'

    return redirect('%s#posts' % tumblr_url, code=301)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=app_config.DEBUG)
